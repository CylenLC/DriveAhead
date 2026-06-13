from driveahead.content.vehicles import VEHICLES
from driveahead.physics.vehicle import BODY_CENTER_OF_GRAVITY_Y_FACTOR, wheel_local_positions


def test_vehicle_specs_have_required_tuning_ranges():
    assert len(VEHICLES) >= 3
    keys = {vehicle.key for vehicle in VEHICLES}
    assert keys == {"buggy", "truck", "sport"}

    for vehicle in VEHICLES:
        assert vehicle.body_mass > 0
        assert vehicle.wheel_mass > 0
        assert vehicle.engine_force > 0
        assert vehicle.air_rotation_torque > 0
        assert vehicle.suspension_stiffness > 0
        assert vehicle.suspension_damping > 0


def test_vehicle_specs_cover_light_and_heavy_handling():
    masses = {vehicle.key: vehicle.body_mass for vehicle in VEHICLES}
    assert masses["buggy"] < masses["truck"]
    assert masses["sport"] < masses["truck"]


def test_vehicle_wheels_sit_visibly_below_body():
    for vehicle in VEHICLES:
        front_wheel, rear_wheel = wheel_local_positions(vehicle)
        body_bottom_y = vehicle.body_size[1] / 2
        wheel_top_y = front_wheel.y - vehicle.wheel_radius

        assert front_wheel.y == rear_wheel.y
        assert wheel_top_y >= body_bottom_y


def test_vehicle_center_of_gravity_is_tuned_low_for_stability():
    assert BODY_CENTER_OF_GRAVITY_Y_FACTOR > 0.35
    assert BODY_CENTER_OF_GRAVITY_Y_FACTOR < 0.55
