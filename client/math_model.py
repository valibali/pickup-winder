import numpy as np
import pyvista as pv

# Parameters
R = 0.005  # Radius of the bobbin without flanges
flange_height = 0.001  # Height of the flanges at each end
scale = 1/10
d = 0.0000635 / scale  # Diameter of the wire
L = 0.06  # Length of the bobbin core
total_turns = 10000 * scale
angle = np.radians(0)  # Taper angle

# Calculate turns per layer and total number of layers
turns_per_length = int(np.floor(L / d))
total_no_layers = np.floor(total_turns / turns_per_length)
flange_radius = (total_no_layers + 10) * d  # Flange radius, slightly larger than the bobbin radius

# Generate turns
turns = np.linspace(0, 2 * np.pi * total_turns, 10000)
x = []
y = []
z = []

def getxmax(angle, current_layer_index):
    if not angle < 0:
        return L
    remaining_height = (total_no_layers * d) - (current_layer_index * d)
    return min(remaining_height / (-np.tan(angle)), L)

for t in turns:
    current_layer_index = np.floor(t / (2 * np.pi * turns_per_length))
    xmax = getxmax(angle, current_layer_index)
    z.append(xmax - np.abs(xmax - 2 * xmax * (t / (2 * np.pi) % (turns_per_length * 2)) / (turns_per_length * 2)))
    x.append((R + current_layer_index * d) * np.cos(t))
    y.append((R + current_layer_index * d) * np.sin(t))

# PyVista visualization
plotter = pv.Plotter()
points = np.column_stack((x, y, z))
spline = pv.Spline(points, 100000)
tube = spline.tube(radius=d/2)
plotter.add_mesh(tube, color='gold', specular=1, smooth_shading=True)

# Adding bobbin with flanges
bobbin_core = pv.Cylinder(center=(0, 0, L/2), direction=(0, 0, 1), radius=R, height=L)
plotter.add_mesh(bobbin_core, color='black', opacity=1, specular=0.6)
flange1 = pv.Cylinder(center=(0, 0, 0), direction=(0, 0, -1), radius=flange_radius, height=flange_height)
flange2 = pv.Cylinder(center=(0, 0, L), direction=(0, 0, 1), radius=flange_radius, height=flange_height)
plotter.add_mesh(flange1, color='black', opacity=1, specular=0.6)
plotter.add_mesh(flange2, color='black', opacity=1, specular=0.6)

# Display settings
plotter.show_grid(color='black')
plotter.enable_3_lights()
plotter.set_background('white')
plotter.show()
