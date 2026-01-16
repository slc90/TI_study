from simnibs import run_simnibs, sim_struct

print("Start")
# Initalize a session
s = sim_struct.SESSION()
# Name of head mesh
s.subpath = "./data/m2m_ernie"
# Output folder
s.pathfem = "./output"
# Initialize a tDCS simulation
tdcslist = s.add_tdcslist()
# Set currents
tdcslist.currents = [-1e-3, 1e-3]
# Initialize the cathode
cathode = tdcslist.add_electrode()
# Connect electrode to first channel (-1e-3 mA, cathode)
cathode.channelnr = 1
# Electrode dimension
cathode.dimensions = [50, 70]
# Rectangular shape
cathode.shape = "rect"
# 5mm thickness
cathode.thickness = 5
# Electrode Position
cathode.centre = "C3"
# Electrode direction
cathode.pos_ydir = "Cz"
# Add another electrode
anode = tdcslist.add_electrode()
# Assign it to the second channel
anode.channelnr = 2
# Electrode diameter
anode.dimensions = [30, 30]
# Electrode shape
anode.shape = "ellipse"
# 5mm thickness
anode.thickness = 5
# Electrode position
anode.centre = "C4"
run_simnibs(s)
print("End")
