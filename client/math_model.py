import numpy as np
import pyvista as pv
import matplotlib.pyplot as plt

# Parameters
R = 0.005  # Radius of the bobbin without flanges
flange_height = 0.001  # Height of the flanges at each end
scale = 1 / 10
angle_scale = 1 / 20
angle_steps = int(360 * angle_scale)
d = 0.0000635 / scale  # Diameter of the wire
L = 0.05  # Length of the bobbin core
l = L - d  # length of the coil (bobbin length - two half wire diameter)
planned_turns = 10000
turns_per_length = int(np.floor(l / d))
total_turns = int(np.ceil(planned_turns / turns_per_length) * turns_per_length * scale)
angle = np.radians(0)  # Taper angle

# Calculate turns per layer and total number of layers
total_no_layers = int(np.ceil(total_turns / turns_per_length))
flange_radius = (
    total_no_layers + 10
) * d  # Flange radius, slightly larger than the bobbin radius

print(f"Total no. of layers: {total_no_layers}")
print(f"Planned turns: {planned_turns}")
print(f"Total turns: {total_turns}")
print(f"Turns per layer: {turns_per_length}")
print(f"Scale: {scale}")
print(f"Angular scale: {angle_scale}")

# Generate turns
turns = np.linspace(0, 2 * np.pi * total_turns, total_turns * angle_steps)
x = []
y = []
z = []
x_intersection = []
y_intersection = []
z_actual = 0
current_layer_index = 0


def getxmax(angle, current_layer_index):
    if not angle < 0:
        return L - d / 2
    remaining_height = ((total_no_layers * d) - (current_layer_index * d)) - d / 2
    return min(remaining_height / (-np.tan(angle)), l) + d / 2


def triangular_wave(x, xm, p):
    return 2 * xm / p * (p * abs((x / p) - np.floor(x / p + 0.5)))


# Setting up the plot
fig, ax = plt.subplots(figsize=(6, 6))

for i in range(total_turns):
    turn = turns[i * angle_steps : (i + 1) * angle_steps]
    current_layer_index = int(np.floor(turn[0] / (2 * np.pi * turns_per_length)))
    xmax = getxmax(angle, current_layer_index)
    turns_per_layer = int(np.floor(xmax / d))
    x_wire = (
        triangular_wave(turn[0] / (2 * np.pi), xmax, turns_per_length * 2)
        + d / 2
        - (current_layer_index % 2) * d / 2
    )
    y_wire = current_layer_index * d + d / 2
    x_intersection.append(x_wire)
    y_intersection.append(y_wire)
    circle = plt.Circle((x_wire, y_wire), d / 2, color="blue", fill=False)
    ax.add_patch(circle)

    for t in turn:
        z.append(
            triangular_wave(t / (2 * np.pi), xmax, turns_per_length * 2)
            + d / 2
            - (current_layer_index % 2) * d / 2
        )
        x.append((R + current_layer_index * d) * np.cos(t))
        y.append((R + current_layer_index * d) * np.sin(t))


# Set the aspect of the plot to be equal
ax.set_aspect("equal", adjustable="box")

# Set title and labels
ax.set_title("Intersections of the Wire with the XY Plane")
ax.set_xlabel("X Coordinate")
ax.set_ylabel("Y Coordinate")

# Grid
ax.grid(True)

# # Setting limits for better control and visualization
# # These should be adjusted based on your actual data range
ax.set_xlim(0, L)
ax.set_ylim(0, (total_no_layers * d))

# Show plot
plt.show()

# PyVista visualization
plotter = pv.Plotter()
points = np.column_stack((x, y, z))
spline = pv.Spline(points, 100 * total_turns)
tube = spline.tube(radius=d / 2)
plotter.add_mesh(tube, color="gold", specular=1, smooth_shading=True)

# Adding bobbin with flanges
bobbin_core = pv.Cylinder(
    center=(0, 0, L / 2), direction=(0, 0, 1), radius=R - d / 2, height=L
)
plotter.add_mesh(bobbin_core, color="black", opacity=1, specular=0.6)
flange1 = pv.Cylinder(
    center=(0, 0, 0 - flange_height / 2),
    direction=(0, 0, 1),
    radius=flange_radius,
    height=flange_height,
)
flange2 = pv.Cylinder(
    center=(0, 0, L + flange_height / 2),
    direction=(0, 0, 1),
    radius=flange_radius,
    height=flange_height,
)
plotter.add_mesh(flange1, color="black", opacity=0.5, specular=0.6)
plotter.add_mesh(flange2, color="black", opacity=0.5, specular=0.6)

# Display settings
plotter.show_grid(color="black")
plotter.enable_3_lights()
plotter.set_background("white")
plotter.show()
