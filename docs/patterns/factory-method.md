# Factory Method — Smart Greenhouse

## Problem

The application needs to create different types of sensors, such as moisture and light sensors. Creating each sensor directly inside the API would make the code harder to change and maintain.

## Solution

The Factory Method pattern uses a common `SensorCreator` interface. Each concrete creator is responsible for creating one type of sensor and its default configuration.

The application chooses the correct creator based on the requested sensor type.

## Code paths

- `backend/src/domain/sensors/entity.py` — Sensor entity
- `backend/src/domain/sensors/creators.py` — Factory Method and concrete creators
- `backend/src/application/sensors/service.py` — Sensor creation service
- `backend/src/infrastructure/persistence/device_repository.py` — Database persistence
- `backend/src/interfaces/api/sensors.py` — REST API

The main creators are:

- `MoistureSensorCreator`
- `LightSensorCreator`

The `get_creator()` function selects the correct creator for `"moisture"` or `"light"`.

## Why use Factory Method?

It keeps sensor creation separate from the API and service logic. New sensor types can be added by creating another creator without putting sensor-specific creation code directly in the API handler.

## Exercise: Temperature Sensor

As an extension exercise, add a `TemperatureSensorCreator`.

It should:

1. Inherit from `SensorCreator`.
2. Implement `create_sensor()`.
3. Use `device_type="temperature_sensor"`.
4. Define its own default configuration.
5. Add `"temperature"` to the creator registry.
6. Add a test for the new creator.