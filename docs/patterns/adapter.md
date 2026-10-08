\# Adapter Pattern — Smart Greenhouse



\## Purpose



The Adapter pattern is used to make different sensor and actuator implementations work with the same application interfaces.



In the Smart Greenhouse application, the domain uses `SensorPort` and `ActuatorPort` as stable interfaces. The infrastructure layer provides adapters for different sensor sources and actuator implementations.



This keeps the application logic independent from specific hardware or external protocols.



\## SensorPort



`SensorPort` is the common interface for sensors.



It defines a `read()` operation that returns a normalized `Reading` object.



The application does not need to know how the sensor value was produced. It only works with the `Reading` returned by the port.



\## Sensor Adapters



\### SimulationSensorAdapter



`SimulationSensorAdapter` generates sensor values without physical hardware.



It supports the greenhouse simulation sensors, such as:



\* Soil moisture

\* Light



For example, soil moisture values are generated in a valid VWC range and light values are generated in lux.



The adapter returns a `Reading` with the source set to `simulation`.



\### VendorStubAdapter



`VendorStubAdapter` represents a future vendor or hardware implementation.



It uses a small internal stub payload instead of communicating with real hardware.



It supports the same sensor types as the simulation adapter and converts the vendor data into the common `Reading` format.



The reading source is set to `vendor`.



A separate `driver` setting is used to select this adapter:



```json

{

&#x20; "driver": "vendor\_stub"

}

```



\### MqttSensorAdapter



`MqttSensorAdapter` adapts an incoming MQTT-style dictionary into the application's `Reading` format.



For example:



```json

{

&#x20; "value": 0.42,

&#x20; "unit": "vwc"

}

```



is converted into a normalized reading.



The adapter does not create an MQTT broker connection in this phase. It only performs the translation of an already received payload.



The reading source is set to `mqtt`.



\## Adapter Selection



`adapter\_selector.py` chooses the appropriate adapter from the device configuration.



The selection rules are:



1\. `driver = "vendor\_stub"` selects the vendor stub adapter.

2\. `protocol = "simulation"` selects the simulation adapter.

3\. `protocol = "mqtt"` selects the MQTT adapter.

4\. Unsupported configurations produce an error.



This allows different device implementations to be selected without changing the application service.



\## ReadingIngest



`ReadingIngest` is responsible for recording sensor readings.



It:



1\. Finds the device.

2\. Checks that the device is a sensor.

3\. Selects the appropriate adapter.

4\. Gets or receives a normalized `Reading`.

5\. Saves the reading through `SensorReadingRepository`.

6\. Returns a `ReadingDto` to the API layer.



The repository is the only component responsible for writing persisted sensor readings.



\## ActuatorPort



`ActuatorPort` provides a common interface for actuator commands.



`SimulationActuatorAdapter` implements this interface for simulated actuators.



It does not control physical hardware. Instead, it records the command through logging.



This gives the application a stable actuator interface that can later be connected to real hardware.



\## Simulation Sampling



`SimulationSampler` periodically checks simulation sensors.



A sensor is sampled only when:



\* it belongs to the simulation device family,

\* it is a sensor,

\* tracking is enabled,

\* and its sampling interval has elapsed.



Each successful sample is passed to `ReadingIngest` and persisted in `sensor\_readings`.



The sampler keeps the previous sample time in memory so the timing can be tested without waiting for real time.



\## Database



Sensor readings are stored in the `sensor\_readings` table.



Each reading contains:



\* device ID

\* value

\* unit

\* source

\* recorded timestamp



An index on device ID and recorded timestamp makes it easier to retrieve recent readings for a sensor.



Sampling settings are stored on the device:



\* `sampling\_interval\_seconds`

\* `tracking\_enabled`



The default sampling interval is 300 seconds and the minimum allowed interval is 5 seconds.



\## Benefits



The Adapter pattern makes the system easier to extend.



For example, a future real sensor driver can implement `SensorPort` without changing `ReadingIngest`.



The application can therefore support simulation, vendor hardware, MQTT-based input, and future hardware implementations while keeping the domain and application logic independent from infrastructure details.



