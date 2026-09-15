from src.domain.sensors.creators import (
    LightSensorCreator,
    MoistureSensorCreator,
    get_creator,
)


def test_moisture_sensor_creator():
    sensor = MoistureSensorCreator().create_sensor("Soil sensor")

    assert sensor.device_type == "moisture_sensor"
    assert sensor.display_name == "Soil sensor"
    assert sensor.default_config["unit"] == "vwc"
    assert sensor.default_config["threshold"] == 30


def test_light_sensor_creator():
    sensor = LightSensorCreator().create_sensor("Light sensor")

    assert sensor.device_type == "light_sensor"
    assert sensor.display_name == "Light sensor"
    assert sensor.default_config["unit"] == "lux"
    assert sensor.default_config["threshold"] == 500


def test_get_creator():
    moisture_creator = get_creator("moisture")
    light_creator = get_creator("light")

    assert isinstance(moisture_creator, MoistureSensorCreator)
    assert isinstance(light_creator, LightSensorCreator)


def test_unknown_sensor_type():
    try:
        get_creator("temperature")
        assert False
    except ValueError:
        assert True