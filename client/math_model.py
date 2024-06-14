import numpy as np
import pyvista as pv
import matplotlib.pyplot as plt
import logging
from typing import Tuple, List

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class BobbinSimulation:
    def __init__(
        self,
        radius: float,
        flange_height: float,
        wire_diameter: float,
        bobbin_length: float,
        planned_turns: int,
        scale: float,
        angle_scale: float,
    ):
        self.radius = radius
        self.flange_height = flange_height
        self.wire_diameter = wire_diameter / scale
        self.bobbin_length = bobbin_length
        self.planned_turns = planned_turns
        self.scale = scale
        self.angle_scale = angle_scale
        self.angle_steps = int(360 * angle_scale)
        self.angle = np.radians(0)  # Taper angle
        self.l = bobbin_length - self.wire_diameter
        self.turns_per_length = int(np.floor(self.l / self.wire_diameter))
        self.total_turns = int(
            np.floor(planned_turns / self.turns_per_length)
            * self.turns_per_length
            * scale
        )
        self.total_no_layers = int(np.ceil(self.total_turns / self.turns_per_length))
        self.flange_radius = (self.total_no_layers + 10) * self.wire_diameter
        self.turns = np.linspace(
            0, 2 * np.pi * self.total_turns, self.total_turns * self.angle_steps
        )
        logging.info(
            f"Initialized BobbinSimulation with {self.total_turns} turns and {self.total_no_layers} layers. - scaled to 1/{int(1/scale)}"
        )

    def xmax(self, angle: float, current_layer_index: int) -> float:
        if angle >= 0:
            return self.bobbin_length - self.wire_diameter / 2
        remaining_height = (
            (self.total_no_layers * self.wire_diameter)
            - (current_layer_index * self.wire_diameter)
        ) - self.wire_diameter / 2
        return min(remaining_height / (-np.tan(angle)), self.l) + self.wire_diameter / 2

    def triangular_wave(self, x: float, xm: float, p: float) -> float:
        return 2 * xm / p * (p * abs((x / p) - np.floor(x / p + 0.5)))

    def plot_intersections(self):
        fig, ax = plt.subplots(figsize=(6, 6))
        x_intersection, y_intersection = [], []

        for i in range(self.total_turns):
            turn = self.turns[i * self.angle_steps : (i + 1) * self.angle_steps]
            current_layer_index = int(
                np.floor(turn[0] / (2 * np.pi * self.turns_per_length))
            )
            xmax = self.xmax(self.angle, current_layer_index)
            x_wire = (
                self.triangular_wave(
                    turn[0] / (2 * np.pi), xmax, self.turns_per_length * 2
                )
                + self.wire_diameter / 2
                - (current_layer_index % 2) * self.wire_diameter / 2
            )
            y_wire = current_layer_index * self.wire_diameter + self.wire_diameter / 2
            x_intersection.append(x_wire)
            y_intersection.append(y_wire)
            circle = plt.Circle(
                (x_wire, y_wire), self.wire_diameter / 2, color="blue", fill=False
            )
            ax.add_patch(circle)

        ax.set_aspect("equal", adjustable="box")
        ax.set_title("Intersections of the Wire with the XY Plane")
        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")
        ax.grid(True)
        ax.set_xlim(0, self.bobbin_length)
        ax.set_ylim(0, (self.total_no_layers * self.wire_diameter))
        plt.show()

    def visualize_3d(self):
        plotter = pv.Plotter()
        x, y, z = [], [], []

        for i in range(self.total_turns):
            turn = self.turns[i * self.angle_steps : (i + 1) * self.angle_steps]
            current_layer_index = int(
                np.floor(turn[0] / (2 * np.pi * self.turns_per_length))
            )
            xmax = self.xmax(self.angle, current_layer_index)
            z_wire = (
                self.triangular_wave(
                    turn[0] / (2 * np.pi), xmax, self.turns_per_length * 2
                )
                + self.wire_diameter / 2
                - (current_layer_index % 2) * self.wire_diameter / 2
            )
            for t in turn:
                x.append(
                    (self.radius + current_layer_index * self.wire_diameter) * np.cos(t)
                )
                y.append(
                    (self.radius + current_layer_index * self.wire_diameter) * np.sin(t)
                )
                z.append(z_wire)

        points = np.column_stack((x, y, z))
        spline = pv.Spline(points, 100 * self.total_turns)
        tube = spline.tube(radius=self.wire_diameter / 2)
        plotter.add_mesh(tube, color="gold", specular=1, smooth_shading=True)

        # Adding flanges
        flange1 = pv.Cylinder(
            center=(0, 0, 0 - self.flange_height / 2),
            direction=(0, 0, 1),
            radius=self.flange_radius,
            height=self.flange_height,
        )
        flange2 = pv.Cylinder(
            center=(0, 0, self.bobbin_length + self.flange_height / 2),
            direction=(0, 0, 1),
            radius=self.flange_radius,
            height=self.flange_height,
        )
        plotter.add_mesh(flange1, color="black", opacity=0.5, specular=0.6)
        plotter.add_mesh(flange2, color="black", opacity=0.5, specular=0.6)

        plotter.show()


# Usage
bobbin_sim = BobbinSimulation(
    radius=0.005,
    flange_height=0.001,
    wire_diameter=0.0000635,
    bobbin_length=0.05,
    planned_turns=10000,
    scale=1 / 10,
    angle_scale=1 / 20,
)
bobbin_sim.plot_intersections()
bobbin_sim.visualize_3d()
