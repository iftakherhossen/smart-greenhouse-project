# Phase 5 — Adapter questions

**Pattern / focus:** Adapter.

**Read first:** [Guide 05](../../materials/guides/05-adapter.md) · [Requirements](requirements.md)

## How to answer

* Use your own wording. Do not paste teaching-example types (for example a legacy XML calendar client) as if they were your greenhouse classes.
* When a question asks about *this application*, refer to sensor ports, adapters, readings, and `sensor_readings` from the lab.
* Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
* Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Adapter in plain language. What problem appears when business code speaks a vendor or legacy protocol (odd field names, units, XML, status codes) directly?

> [!NOTE]
> ***Your Answer***
>
> The purpose of Adapter is to make an existing interface work with another interface that has a different format. Without an adapter, the application code would need to understand vendor-specific field names, units, protocols, or other formats directly. This would make the code harder to maintain and change.

2. Name the participants (**target / port**, **adaptee**, **adapter**, **client**). What does the adapter translate, and what must it **not** decide (business policy)?

> [!NOTE]
> ***Your Answer***
>
> The target or port is the interface the application expects, the adaptee is the existing system or data format, the adapter connects the two, and the client uses the target interface. The adapter translates data and interface details into the format expected by the application. It should not decide business rules or policies, such as when irrigation should start.

3. GoF distinguishes an **object adapter** (composition) from a **class adapter** (inheritance). Which does modern code prefer, and why?

> [!NOTE]
> ***Your Answer***
>
> Modern code usually prefers an object adapter because it uses composition instead of inheritance. This makes the adapter more flexible because it can wrap different implementations without creating a strong dependency on a specific class hierarchy.

## B. This phase of the application

4. What is `SensorPort` in this lab, and what normalized value type (for example `Reading`) do adapters return? Why do application services depend on the port rather than on a simulation driver or vendor SDK?

> [!NOTE]
> ***Your Answer***
>
> `SensorPort` is the common interface that sensor adapters use to provide readings to the application. The adapters return a normalized `Reading` containing the device ID, value, unit, source, and recorded time. Application services depend on the port so they do not need to know whether the reading came from a simulation, vendor device, or another protocol.

5. You need three translations onto the same normalized reading: a simulation adapter, a vendor stub, and an MQTT translator that accepts a payload dict. Why is the different raw shape the point of the exercise? How does `source` (`simulation`, `vendor`, or `mqtt`) show which adapter produced the reading, and why must the MQTT translator not open a broker in this phase? Phase 12 may deliver that same dict on a device HTTP route or through an optional broker — why must this phase still not open either transport?

> [!NOTE]
> ***Your Answer***
>
> The different raw shapes show why an adapter is useful. The simulation, vendor stub, and MQTT data can have different formats, but they are converted into the same `Reading` type for the rest of the application. The `source` value records where the reading came from, such as `simulation`, `vendor`, or `mqtt`. The MQTT adapter should only translate the payload in this phase and should not open a broker or HTTP connection because transport is outside the Adapter pattern being implemented here. Phase 12 can handle the actual transport later.

6. Readings are **appended** to `sensor_readings` (history grows). Why not keep only the latest value in memory or overwrite a single row, and which later phase consumes this history? Why do a manual read, the simulation sampler, and (later) MQTT share **one** writer of that table? Why does the sampler skip devices with tracking off and MQTT devices, and why do sensor cards poll the latest stored reading until Phase 12?

> [!NOTE]
> ***Your Answer***
>
> Readings are stored as history because the application may need to compare previous values and use the data in later phases. Keeping only the latest value would lose the history. The later monitoring and automation phases can use these stored readings. A manual read, the simulation sampler, and later MQTT should use the same writer so that readings are stored in one consistent way. The sampler skips devices with tracking disabled because the user has chosen not to collect automatic readings. It also does not handle MQTT devices because MQTT is only a translator in this phase. The sensor cards poll the latest stored reading as a temporary solution until Phase 12 introduces WebSocket updates.

7. `POST /api/sensors/{id}/read` runs an adapter, persists, and returns a DTO. What HTTP status is appropriate when the device is missing versus when the adapter fails? Why must the router never see vendor-shaped types?

> [!NOTE]
> ***Your Answer***
>
> If the device does not exist, the API should return **404 Not Found** because the requested resource cannot be found. If the adapter fails because of invalid configuration or an unsupported sensor type, the API should return **400 Bad Request**. The router should only work with the normalized `Reading` and DTO types so that vendor-specific data formats do not spread into the API layer.

## C. Compare, contrast, and scenarios

8. Contrast Adapter with **Facade**. Adapter changes the **shape** of an existing interface; Facade simplifies **how to use** a subsystem. Give a greenhouse-shaped example of each (Adapter this phase; Facade in Phase 7).

> [!NOTE]
> ***Your Answer***
>
> An Adapter changes one interface or data format into another interface that the application already expects. In this phase, the vendor and MQTT adapters convert their different sensor data into a common `Reading`. A Facade is different because it provides a simpler interface for using several parts of a subsystem. In the greenhouse, a Phase 7 facade could provide one simple service for managing several greenhouse configuration or device operations instead of making the client call each subsystem separately.

9. Contrast Adapter with **Decorator**. Both wrap an object. What is different about the interface they present to the client?

> [!NOTE]
> ***Your Answer***
>
> An Adapter changes the interface so that an incompatible object can be used by the client. A Decorator keeps the same interface but adds extra behavior around the existing object. For example, an adapter could convert vendor sensor data into a `Reading`, while a decorator could add logging or timing around a sensor that already uses the correct interface.

10. A classmate puts irrigation policy (“if moisture < 0.3 then water”) inside the vendor adapter. Why is that a trap? Where should that decision live instead (later Strategy), and what should stay in the adapter?

> [!NOTE]
> ***Your Answer***
>
> This is a trap because the adapter should only translate the vendor data into the format used by the application. If irrigation rules are placed inside it, the adapter becomes responsible for business logic and becomes harder to reuse or replace. The irrigation decision should be handled by a later Strategy implementation. The adapter should only handle things such as converting values, units, field names, and vendor-specific formats into the common application format.
