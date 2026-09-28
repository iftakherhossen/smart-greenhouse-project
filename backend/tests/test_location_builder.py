import pytest

from src.domain.locations.config_builder import LocationConfigBuilder
from src.domain.locations.errors import ConfigurationError


def test_builder_creates_valid_location_config():
    config = (
        LocationConfigBuilder()
        .with_location_name("Test Greenhouse")
        .add_zone(
            name="Zone A",
            moisture_threshold_low=0.3,
            moisture_threshold_high=0.7,
            schedule={"watering": "08:00"},
        )
        .build()
    )

    assert config.location.name == "Test Greenhouse"
    assert len(config.location.zones) == 1
    assert config.location.zones[0].name == "Zone A"
    assert config.location.zones[0].moisture_threshold_low == 0.3
    assert config.location.zones[0].moisture_threshold_high == 0.7
    assert config.location.zones[0].schedule == {
        "watering": "08:00"
    }


def test_builder_rejects_missing_location_name():
    builder = LocationConfigBuilder()

    with pytest.raises(
        ConfigurationError,
        match="Location name is required",
    ):
        builder.build()


def test_builder_rejects_location_without_zones():
    builder = LocationConfigBuilder()

    builder.with_location_name("Test Greenhouse")

    with pytest.raises(
        ConfigurationError,
        match="At least one zone is required",
    ):
        builder.build()


def test_builder_rejects_invalid_threshold_order():
    builder = LocationConfigBuilder()

    builder.with_location_name("Test Greenhouse")

    with pytest.raises(
        ConfigurationError,
        match="Low moisture threshold must be lower than high threshold",
    ):
        builder.add_zone(
            name="Zone A",
            moisture_threshold_low=0.8,
            moisture_threshold_high=0.4,
        )


def test_builder_rejects_threshold_outside_valid_range():
    builder = LocationConfigBuilder()

    builder.with_location_name("Test Greenhouse")

    with pytest.raises(
        ConfigurationError,
        match="Low moisture threshold must be between 0.0 and 1.0",
    ):
        builder.add_zone(
            name="Zone A",
            moisture_threshold_low=-0.1,
            moisture_threshold_high=0.7,
        )


def test_builder_rejects_duplicate_zone_names():
    builder = LocationConfigBuilder()

    builder.with_location_name("Test Greenhouse")

    builder.add_zone(
        name="Zone A",
        moisture_threshold_low=0.3,
        moisture_threshold_high=0.7,
    )

    with pytest.raises(
        ConfigurationError,
        match="must be unique within the location",
    ):
        builder.add_zone(
            name="Zone A",
            moisture_threshold_low=0.4,
            moisture_threshold_high=0.8,
        )