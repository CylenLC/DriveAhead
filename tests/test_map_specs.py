from driveahead.content.maps import MAPS


def test_map_specs_are_valid_for_two_player_matches():
    assert len(MAPS) >= 3

    for map_spec in MAPS:
        assert set(map_spec.spawn_points) == {1, 2}
        assert len(map_spec.terrain_segments) >= 3
        assert map_spec.hazards == ()
        assert map_spec.entities == ()
        min_x, min_y, max_x, max_y = map_spec.camera_bounds
        assert min_x < max_x
        assert min_y < max_y


def test_map_keys_are_unique():
    keys = [map_spec.key for map_spec in MAPS]
    assert len(keys) == len(set(keys))
