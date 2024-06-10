import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pyvista as pv

# Revised parameters and model using a triangular wave function for z
scale = 1/10

R = 0.005  # Radius of the bobbin
d = 0.0000635 / scale  # Diameter of the wire
L = 0.06  # Effective visual length of the bobbin
total_turns = 10000 * scale
turns_per_length = (np.floor(L / d))  # Turns needed to cover the bobbin length once
angle = np.radians(85)  # Angle of the cone in degrees converted to radians

print(f'Turns per layer: {turns_per_length}')
print(f'Total turns: {total_turns}')

# Generate the turns for multiple periods
turns = np.linspace(0, 2 * np.pi * total_turns, 10000)

# Prepare figure for updated visualization
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

x = []
y = []
z = []
xmin = 0

b = L  # Initial value of xmax when there are no layers
a = 5  # Change in xmax per unit increase in the height of the current layer


def getxmax(angle, current_layer_index, offset):
    height = (current_layer_index * d + offset)
    # Calculate xmax using the conical shape formula
    #return L - (xmin + height * np.tan(angle))
    return L


for t in turns:
    current_layer_index = np.floor(t / (2 * np.pi * turns_per_length))

    # Calculate z using a triangular wave function
    # Calculate z using a refactored triangular wave function using xmin and xmax
    xmax = getxmax(angle, current_layer_index, 3*d)
    z.append(xmax - np.abs(xmax - 2 * (xmax - xmin) * (t / (2 * np.pi) % (turns_per_length * 2)) / (turns_per_length * 2)))


    # Calculate x and y for cylindrical to cartesian conversion
    x.append((R + current_layer_index * d) * np.cos(t))
    y.append((R + current_layer_index * d) * np.sin(t))

# Create a PyVista plotter instance
plotter = pv.Plotter()

# Create a tube representing the wire
points = np.column_stack((x, y, z))
spline = pv.Spline(points, 100000)
tube = spline.tube(radius=d/2)
plotter.add_mesh(tube, color='orange', specular=1, smooth_shading=True)

# Optionally, add a cylindrical bobbin (for context)
cylinder = pv.Cylinder(center=(0, 0, L/2), direction=(0, 0, 1), radius=R, height=L)
plotter.add_mesh(cylinder, color='lightgrey', opacity=0.5, specular=0.6)

# Set up the camera and display settings
plotter.show_grid(color='black')
plotter.enable_3_lights()
plotter.set_background('white')
plotter.show()