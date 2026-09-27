# Abstract Factory — Smart Greenhouse

## Problem

A greenhouse system operates in distinct environments: simulated hardware for in-memory testing and physical edge hardware (Raspberry Pi/microcontrollers) in production. 

Each environment requires a cohesive family of compatible products (sensors and actuators). Instantiating devices with hardcoded configurations or ad-hoc conditionals across services would risk mixing incompatible protocols (for example, pairing a physical SPI bus configuration with an in-memory simulation actuator).

## Solution

The Abstract Factory pattern provides an interface (`DeviceFamilyFactory`) declaring factory methods for creating families of related or dependent objects without specifying their concrete classes.

- Concrete factories (`SimulationDeviceFactory`, `EdgeHardwareFactory`) produce family-consistent sets of sensors and actuators.
- Each concrete factory composes existing domain creators (from Phase 2's Factory Method) and configures bus communication protocols tailored to the runtime environment (`sim_virtual_bus` vs `i2c`/`spi`/`gpio-relay`/`pwm`).
- The application selects and executes factories dynamically via a registry lookup (`get_family_factory`).

## Code Paths

- `backend/src/domain/devices/entity.py` — Device entity supporting roles (`sensor`, `actuator`) and families
- `backend/src/domain/devices/family_factory.py` — Abstract Factory interface, concrete family factories, and factory registry
- `backend/src/application/devices/family_service.py` — Application service coordinating provisioning and queries
- `backend/src/application/devices/dto.py` & `mappers.py` — Data transfer objects and entity mappers
- `backend/src/infrastructure/persistence/device_repository.py` — Repository handling persistence and multi-criteria filtering
- `backend/src/interfaces/api/devices.py` — REST endpoints (`GET /api/devices`, `POST /api/devices/provision`)
- `frontend/src/components/devices/DeviceFamilySwitcher.tsx` — Environment switcher UI
- `frontend/src/components/devices/DeviceList.tsx` — Device catalogue with role/family badges and configuration views

## Why Use Abstract Factory?

1. **Family Consistency:** Guarantees that all devices provisioned together share identical communication protocols and compatibility constraints.
2. **Open/Closed Principle:** Adding a new device family (such as `cloud` or `lorawan`) requires creating a new subclass of `DeviceFamilyFactory` and registering it, without modifying client provisioning logic.
3. **Layer Decoupling:** API endpoints and application services depend exclusively on the abstract interface, keeping domain instantiation logic decoupled from HTTP transport and persistence layers.
