import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from mealpy import Problem, FloatVar, IntegerVar, BinaryVar, CategoricalVar

class GreyhavenProblem(Problem):
    
    def __init__(self, situation="Initial response", assignment="B"):

        # Equipment depot location
        self.equipment_depot = (5.0, 0.0)

        # Demand points: (x, y, type, base_weight)
        self.demand_points = [
            (0.8, 1.2, "Residential", 4),
            (2.0, 1.8, "Shelter", 8),
            (4.6, 1.0, "Depot", 5),
            (7.0, 1.5, "Residential", 4),
            (9.0, 0.8, "Clinic", 10),
            (1.0, 4.2, "Clinic", 10),
            (2.8, 3.4, "Residential", 4),
            (5.0, 4.5, "Shelter", 8),
            (7.4, 3.6, "Depot", 5),
            (9.2, 4.8, "Residential", 4),
            (0.7, 7.2, "Residential", 4),
            (3.2, 6.4, "Shelter", 8),
            (5.6, 7.1, "Clinic", 10),
            (8.5, 6.5, "Residential", 4),
            (1.8, 9.0, "Depot", 5),
            (4.0, 8.8, "Residential", 4),
            (7.0, 9.3, "Shelter", 8),
            (9.3, 8.8, "Residential", 4)
        ]

        # Operating situations
        self.situations = {
            "Initial response": {
                "multipliers": {
                    "Residential": 1,
                    "Shelter": 1,
                    "Clinic": 1,
                    "Depot": 1
                },
                "nu0": 0.04,
                "rho": 0,
                "a": 5,
                "b": 5
            },

            "Evening pressure": {
                "multipliers": {
                    "Residential": 1,
                    "Shelter": 2,
                    "Clinic": 2,
                    "Depot": 1
                },
                "nu0": 0.04,
                "rho": 3,
                "a": 5,
                "b": 5
            },

            "Northern outage": {
                "multipliers": {
                    "Residential": 2,
                    "Shelter": 1,
                    "Clinic": 2,
                    "Depot": 1
                },
                "nu0": 0.06,
                "rho": 2,
                "a": 7,
                "b": 8
            }
        }

        self.set_situation(situation)

        self.assignment = assignment

        # 4 stations × 6 variables = 24 decision variables
        bounds = []

        for i in range(4):
            bounds.extend([
                FloatVar(lb=0, ub=10, name=f"x{i}"),
                FloatVar(lb=0, ub=10, name=f"y{i}"),
                FloatVar(lb=0.2, ub=2, name=f"p{i}")
            ])

            if assignment == "A":
                bounds.extend([
                    IntegerVar(lb=4, ub=4, name=f"h{i}"),
                    CategoricalVar(valid_sets=(1,), name=f"c{i}"),
                    BinaryVar(n_vars=1, name=f"z{i}")
                ])

            else:
                bounds.extend([
                    IntegerVar(lb=2, ub=6, name=f"h{i}"),
                    CategoricalVar(valid_sets=(1, 2, 3), name=f"c{i}"),
                    BinaryVar(n_vars=1, name=f"z{i}")
                ])

        super().__init__(bounds=bounds, minmax="min")

    def set_situation(self, situation):
        if situation not in self.situations:
            raise ValueError("Unknown operating situation")

        self.current_situation = situation
        self.parameters = self.situations[situation]

    def get_demand_weights(self):
        """Calculate updated demand priorities for the current situation."""

        weights = []

        for x, y, point_type, base_weight in self.demand_points:
            multiplier = self.parameters["multipliers"][point_type]
            weights.append(base_weight * multiplier)

        return np.array(weights)

    def calculate_background_interference(self):
        """Calculate background interference at all demand points."""

        nu0 = self.parameters["nu0"]
        rho = self.parameters["rho"]
        a = self.parameters["a"]
        b = self.parameters["b"]

        interference = []

        for x, y, _, _ in self.demand_points:
            distance_squared = (x - a)**2 + (y - b)**2

            nu = nu0 * (
                1 + rho * np.exp(-distance_squared / 8)
            )

            interference.append(nu)

        return np.array(interference)

    
    def calculate_distances(self, stations):
        """
        Calculate squared distances between every demand point
        and every station.
        Returns: array with shape (18, 4)
        """

        stations = np.asarray(stations).reshape(4, 6)

        demand_xy = np.array([
            (point[0], point[1]) for point in self.demand_points
        ])

        station_xy = stations[:, :2]

        distances_squared = np.sum(
            (demand_xy[:, None, :] - station_xy[None, :, :]) ** 2,
            axis=2
        )

        return distances_squared

    def calculate_received_signal(self, stations):
        """
        Calculate R_ji for every demand point and station.
        Returns: array with shape (18, 4)
        """

        stations = np.asarray(stations).reshape(4, 6)

        distances_squared = self.calculate_distances(stations)

        power = stations[:, 2]
        height = stations[:, 3]
        status = stations[:, 5]

        gain = 1 + 0.5 * (height - 2)

        received_signal = (
            status * power /
            (1 + distances_squared / gain)
        )

        return received_signal

    def calculate_sinr(self, stations):
        """
        Calculate SINR for every demand point and station.
        Returns: array with shape (18, 4)
        """

        stations = np.asarray(stations).reshape(4, 6)

        received = self.calculate_received_signal(stations)

        channels = stations[:, 4]

        # Identify stations operating on the same channel
        same_channel = (
            channels[:, None] == channels[None, :]
        )

        # Total received signal from same-channel stations
        total_same_channel = received @ same_channel.T

        # Exclude each station's own signal
        interference = total_same_channel - received

        background = self.calculate_background_interference()

        sinr = received / (background[:, None] + interference)

        return sinr

    def calculate_service_quality(self, stations):
        """
        Calculate q_j for every demand point.
        Returns: array with shape (18,)
        """

        sinr = self.calculate_sinr(stations)

        quality_per_station = (
            sinr**2 / (1 + sinr**2)
        )

        # Select the best station for each demand point
        service_quality = np.max(quality_per_station, axis=1)

        return service_quality

    def calculate_objective_Q(self, stations):
        """
        Calculate the final objective Q(X).
        Lower (more negative) values are better.
        """

        service_quality = self.calculate_service_quality(stations)

        weights = self.get_demand_weights()

        Q = -np.sum(weights * service_quality) / np.sum(weights)

        return Q

    def obj_func(self, x):
        decoded = self.decode_solution(x)

        stations = np.array([
            [
                decoded[f"x{i}"],
                decoded[f"y{i}"],
                decoded[f"p{i}"],
                decoded[f"h{i}"],
                decoded[f"c{i}"],
                decoded[f"z{i}"]
            ]
            for i in range(4)
        ], dtype=float)

        return self.calculate_objective_Q(stations)

    def calculate_delivery_distances(self, stations):
        """
        Calculate the distance of each station from the equipment depot.
        Returns four distances (L_i).
        """

        stations = np.asarray(stations).reshape(4, 6)

        depot_x, depot_y = self.equipment_depot

        distances = np.sqrt(
            (stations[:, 0] - depot_x) ** 2 +
            (stations[:, 1] - depot_y) ** 2
        )

        return distances

    def calculate_deployment_cost(self, stations):
        """
        Calculate total deployment cost C(X), in dollars.
        """

        stations = np.asarray(stations).reshape(4, 6)

        height = stations[:, 3]
        status = stations[:, 5]

        distances = self.calculate_delivery_distances(stations)

        station_costs = status * (
            400 +
            35 * (height - 2) ** 2 +
            20 * distances
        )

        return np.sum(station_costs)

    def calculate_electrical_energy(self, stations):
        """
        Calculate electrical energy E(X) over 12 hours, in Wh.
        """

        stations = np.asarray(stations).reshape(4, 6)

        power = stations[:, 2]
        height = stations[:, 3]
        status = stations[:, 5]

        station_energy = 12 * status * (
            18 + 14 * power + 0.5 * (height - 2)
        )

        return np.sum(station_energy)

    def calculate_objectives(self, stations):
        """
        Return all three objectives for Assignment C:
        Q(X), C(X), E(X).
        """
        
        Q = self.calculate_objective_Q(stations)
        C = self.calculate_deployment_cost(stations)
        E = self.calculate_electrical_energy(stations)

        return np.array([Q, C, E])

    def plot_deployment(self, stations):

        stations = np.asarray(stations).reshape(4, 6)

        fig, ax = plt.subplots(figsize=(9, 8))
        fig.patch.set_facecolor("#f8f9fa")
        ax.set_facecolor("#ffffff")

        # 1. Plot demand points in black, using different shapes
        markers = {
            "Residential": "o",
            "Shelter": "s",
            "Clinic": "^",
            "Depot": "D"
        }

        for demand_type, marker in markers.items():
            points = [
                p for p in self.demand_points
                if p[2] == demand_type
            ]

            x = [p[0] for p in points]
            y = [p[1] for p in points]

            ax.scatter(
                x, y,
                color="black",
                marker=marker,
                s=75,
                linewidths=0.7,
                label=demand_type,
                zorder=5
            )

        # 2. Plot equipment depot
        ax.scatter(
            *self.equipment_depot,
            marker="s",
            s=150,
            color="#f1c40f",
            linewidths=1.2,
            label="Equipment Depot",
            zorder=7
        )
        ax.annotate(
            f"Equipment Depot",
            self.equipment_depot,
            xytext=(9, 10),
            textcoords="offset points",
            # weight="bold",
            fontsize=10,
            color="black"
        )

        # 3. Plot stations according to their channels
        channel_colors = {
            1: "#e74c3c",
            2: "#2ecc71",
            3: "#3a69d6"
        }

        for i, station in enumerate(stations):
            x, y, power, height, channel, status = station

            if status == 0:
                continue

            color = channel_colors[int(channel)]

            # Plot station
            ax.scatter(
                x,
                y,
                marker="o",
                s=150,
                color=color,
                linewidths=1.5,
                zorder=8
            )

            ax.annotate(
                f"RS{i+1}\nP={power:.2f}, H={height}, C={channel}",
                (x, y),
                xytext=(9, 10),
                textcoords="offset points",
                fontsize=8,
                color="black"
            )

            # Relative signal-strength visualization:
            gain = 1 + 0.5 * (height - 2)
            reference_strength = (
                status * power / (1 + 1 / gain)
            )

            # Circle radius is a visual scale, NOT a coverage radius.
            radius = reference_strength * 2

            ax.add_patch(
                Circle(
                    (x, y),
                    radius,
                    facecolor=color,
                    edgecolor=color,
                    alpha=0.15,
                    linewidth=2
                )
            )

        # 4. Plot settings
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_aspect("equal")

        ax.set_xlabel("Easting (km)")
        ax.set_ylabel("Northing (km)")
        ax.set_title(f"Greyhaven Deployment - {self.current_situation}")

        ax.grid(alpha=0.3)
        ax.legend()
        plt.tight_layout()
        plt.show()

