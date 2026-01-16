# TI正向计算方案

## 1. 概述

时域干涉刺激（Temporal Interference Stimulation, TI）是一种新型的非侵入性深部脑刺激技术。TI正向计算的目标是根据给定的刺激参数（包括电极配置、电流强度、频率等）和个体的头部几何结构，预测脑内电场的空间分布，为理解刺激机制、评估刺激效果和安全性提供定量依据。

本方案基于SimNIBS（Simulation of Non-invasive Brain Stimulation）软件套件，详细介绍TI正向仿真的完整流程和方法。本方案参考SimNIBS官方文档：https://simnibs.github.io/simnibs/build/html/index.html

## 2. 所需工具与数据

### 2.1 软件要求
- **SimNIBS 4.5** 或更高版本
- **Python**（用于脚本化操作，可选）
- **MRI图像处理工具**（如FSL、FreeSurfer，SimNIBS已集成部分功能）

### 2.2 数据要求
- **T1加权 MRI**：用于分割头皮、颅骨、脑脊液、灰质、白质等组织
- **T2加权 MRI**（可选）：提高组织分割精度
- **电极参数**：电极形状、尺寸、位置、注入电流强度、频率等

## 3. 正向仿真流程

### 3.1 头部模型构建

#### 3.1.1 MRI数据预处理
1. **数据格式转换**：将DICOM格式转换为NIfTI格式（可使用`dcm2niix`工具）
2. **图像重定向**：确保图像方向正确
3. **偏置场校正**：消除MRI图像中的强度不均匀性

#### 3.1.2 组织分割
使用SimNIBS的`headreco`工具进行自动化组织分割：
```bash
headreco all --subject <subject_name> --mri <T1_file> --t2 <T2_file> --output <output_dir>
```
分割结果包括：
- 头皮（scalp）
- 颅骨（skull）
- 脑脊液（CSF）
- 灰质（gray matter）
- 白质（white matter）

#### 3.1.3 有限元网格生成
SimNIBS自动将分割结果转换为三维有限元网格：
- 网格分辨率：通常为1-2mm
- 组织电导率分配（单位：S/m）：
  - 头皮：0.465
  - 颅骨：0.010
  - 脑脊液：1.654
  - 灰质：0.275
  - 白质：0.126（各向异性模型需考虑方向依赖性）

### 3.2 TI刺激参数设置

#### 3.2.1 电极配置
时域干涉刺激需要至少两对电极：
- **第一对电极**：施加频率为f₁的高频交流电流（例如2000 Hz）
- **第二对电极**：施加频率为f₂的高频交流电流（例如2010 Hz）
- **差频**：Δf = |f₁ - f₂|（例如10 Hz）

电极参数包括：
1. **电极类型**：圆形、矩形或自定义形状
2. **电极尺寸**：直径/边长（通常1-4 cm²）
3. **电极位置**：在头皮表面的三维坐标（MNI空间或个体空间）
4. **电流强度**：每对电极的注入电流（通常1-2 mA）

#### 3.2.2 参数文件配置
创建SimNIBS配置文件（JSON格式）：
```json
{
  "stimulation_type": "TI",
  "electrodes": [
    {
      "name": "Electrode_A1",
      "position": [x1, y1, z1],
      "shape": "circle",
      "dimensions": [radius],
      "current": 1.0,
      "frequency": 2000
    },
    {
      "name": "Electrode_A2",
      "position": [x2, y2, z2],
      "shape": "circle",
      "dimensions": [radius],
      "current": -1.0,
      "frequency": 2000
    },
    {
      "name": "Electrode_B1",
      "position": [x3, y3, z3],
      "shape": "circle",
      "dimensions": [radius],
      "current": 1.0,
      "frequency": 2010
    },
    {
      "name": "Electrode_B2",
      "position": [x4, y4, z4],
      "shape": "circle",
      "dimensions": [radius],
      "current": -1.0,
      "frequency": 2010
    }
  ],
  "mesh_file": "path/to/mesh.msh",
  "conductivities": {
    "scalp": 0.465,
    "skull": 0.010,
    "csf": 1.654,
    "gray_matter": 0.275,
    "white_matter": 0.126
  }
}
```

### 3.3 电场计算

#### 3.3.1 物理模型
TI刺激的电场计算基于准静态麦克斯韦方程组：
```
∇·(σ∇V) = 0
E = -∇V
```
其中：
- σ：组织电导率张量
- V：电位分布
- E：电场强度

对于TI刺激，总电场为两对电极产生电场的叠加：
```
E_total(r, t) = E₁(r)sin(2πf₁t) + E₂(r)sin(2πf₂t)
```
产生的包络电场（差频分量）为：
```
E_envelope(r, t) ≈ |E₁(r) - E₂(r)| · sin(2πΔf·t + φ)
```

#### 3.3.2 求解方法
SimNIBS使用有限元法（FEM）求解：
1. **离散化**：将计算域离散为有限元网格
2. **组装刚度矩阵**：基于组织电导率和几何形状
3. **施加边界条件**：根据电极电流设置
4. **求解线性方程组**：使用直接法（如PARDISO）或迭代法
5. **计算电场**：从电位分布求梯度

#### 3.3.3 计算执行
通过SimNIBS GUI或命令行执行：
```bash
simnibs <subject_name> <simulation_config.json>
```
或在Python脚本中：
```python
import simnibs

# 读取仿真配置
sim = simnibs.sim_struct.Simulation()
sim.fnamehead = 'path/to/mesh.msh'
sim.fnamecfg = 'path/to/config.json'

# 运行仿真
results = simnibs.run_simulation(sim)
```

### 3.4 结果后处理与分析

#### 3.4.1 电场可视化
1. **三维体积渲染**：显示电场在脑内的空间分布
2. **切片视图**：冠状面、矢状面、水平面视图
3. **等值面图**：显示特定电场强度的等值面
4. **脑表面投影**：将电场强度投影到皮层表面

#### 3.4.2 定量分析指标
1. **最大电场强度**：E_max (V/m)
2. **目标区平均电场**：E_mean_target (V/m)
3. **聚焦指数**：目标区与非目标区电场强度比
4. **激活体积**：超过阈值（如0.5 V/m）的体素数
5. **深度-强度曲线**：电场强度随深度的变化

#### 3.4.3 结果导出格式
- **NIfTI格式**：电场分布体积数据
- **GIfTI格式**：皮层表面投影数据
- **MATLAB .mat格式**：数值结果矩阵
- **CSV格式**：统计指标表格

#### 3.4.4 空间标准化
将个体空间的电场分布转换到标准空间（MNI空间）：
```python
import simnibs.transformations as st

# 将电场结果转换到MNI空间
E_MNI = st.transform_to_mni(E_subject, transformation_matrix)
```
