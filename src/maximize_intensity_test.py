"""Example of optimizaion maximizing intensity in the target

Copyright (c) 2019 SimNIBS developers. Licensed under the GPL v3.
"""

import simnibs

opt = simnibs.opt_struct.TDCSoptimize()
opt.leadfield_hdf = "leadfield/ernie_leadfield_EEG10-10_UI_Jurak_2007.hdf5"
opt.name = "optimization/single_target"

opt.max_total_current = 2e-3
opt.max_individual_current = 1e-3
opt.max_active_electrodes = 8

target = opt.add_target()
target.positions = [-50.7, 5.1, 55.5]
# Set the intensity to a large value (e.g, 100)
# 这里和simple_optimization仅仅只有数值上的区别
# 在 tDCS / tACS 模拟中：
# 典型电极电流：1–2 mA
# 对应的头皮下电场强度：0.1–0.5 V/m（目标脑区）
# 直接设置一个很大的值，优化实际上不可能实现，得到的结果就是focality比较差
# 怎样设置这个值实际上还是只能靠尝试
target.intensity = 100

# Run optimization
simnibs.run_simnibs(opt)
