from __future__ import annotations

from dataclasses import dataclass


Color = tuple[int, int, int]


@dataclass(frozen=True)
class VehicleSpec:
    key: str
    name: str
    body_size: tuple[float, float]
    body_mass: float
    wheel_radius: float
    wheel_mass: float
    engine_force: float
    brake_force: float
    air_rotation_torque: float
    suspension_stiffness: float
    suspension_damping: float
    head_offset: tuple[float, float]
    color: Color


VEHICLES: tuple[VehicleSpec, ...] = (
    VehicleSpec(
        key="buggy",
        name="Buggy",
        body_size=(96, 34),
        body_mass=80,
        wheel_radius=18,
        wheel_mass=12,
        engine_force=60000,
        brake_force=0.78,
        air_rotation_torque=3600000,
        suspension_stiffness=520,
        suspension_damping=52,
        head_offset=(0, -36),
        color=(236, 93, 70),
    ),
    VehicleSpec(
        key="truck",
        name="Truck",
        body_size=(122, 46),
        body_mass=150,
        wheel_radius=22,
        wheel_mass=20,
        engine_force=76000,
        brake_force=0.7,
        air_rotation_torque=2200000,
        suspension_stiffness=760,
        suspension_damping=70,
        head_offset=(8, -45),
        color=(68, 139, 202),
    ),
    VehicleSpec(
        key="sport",
        name="Sport",
        body_size=(108, 30),
        body_mass=95,
        wheel_radius=17,
        wheel_mass=11,
        engine_force=82000,
        brake_force=0.74,
        air_rotation_torque=4300000,
        suspension_stiffness=610,
        suspension_damping=56,
        head_offset=(-4, -34),
        color=(245, 181, 65),
    ),
)


def vehicle_by_key(key: str) -> VehicleSpec:
    for vehicle in VEHICLES:
        if vehicle.key == key:
            return vehicle
    raise KeyError(f"Unknown vehicle: {key}")
