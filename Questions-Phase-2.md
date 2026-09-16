# Phase 2 — Factory Method questions

**Pattern / focus:** Factory Method.

**Read first:** [Guide 02](../../materials/guides/02-factory-method.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example courier notifiers) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to sensors, creators, the `devices` table, and the sensors API from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Factory Method in plain language. What problem appears when callers scatter `new` / constructors (or a growing `if type == ...`) across the application?

> [!NOTE]
> ***Your Answer***
>
> Factory Method helps keep object creation in one place. Without it, we may have many new statements or if/elif checks in different parts of the application, which makes the code harder to maintain.

2. Name the main participants of Factory Method (**product**, **concrete product**, **creator**, **concrete creator**, **client**). For each, give one sentence: what it is responsible for.

> [!NOTE]
> ***Your Answer***
>
> Explaining the methods below:
- Product: The common type or interface for sensors.
- Concrete product: The actual sensor, like MoistureSensor or LightSensor.
- Creator: Defines how a sensor should be created.
- Concrete creator: Creates a specific type of sensor.
- Client: Requests a sensor from the creator instead of creating it directly.

3. How do you add a **new product variant** when creators are polymorphic (new class + registry entry) versus when creation lives in one shared `if/elif` function? Why does that difference matter for extension?

> [!NOTE]
> ***Your Answer***
>
> With polymorphic creators, we can add a new sensor class and register it without changing the main creation logic. With one if/elif function, we have to edit that function every time we add a new type.

## B. This phase of the application

4. In this lab, what is the **product** and what are the **concrete creators**? Why must the API handler (or sensor service) go through a creator/registry instead of constructing `MoistureSensor` / `LightSensor` itself?

> [!NOTE]
> ***Your Answer***
>
> The product is a sensor. The concrete creators are responsible for creating specific sensors, such as moisture and light sensors. The API should use the creator or registry so it does not need to know how each sensor is created.

5. `POST /api/sensors` accepts a short `type` key such as `"moisture"` or `"light"`, while the stored/returned field is `device_type` (for example `moisture_sensor`). Why are those two fields different? Who decides the stored `device_type` and `default_config`?

> [!NOTE]
> ***Your Answer***
>
> type is a short name that the client sends, such as "moisture". device_type is the actual type saved in the database, such as "moisture_sensor". The creator decides the stored device_type and its default configuration.

6. Why is there a single `devices` table with `role="sensor"` instead of a dedicated `sensors` table? What later phase does that choice prepare for?

> [!NOTE]
> ***Your Answer***
>
> One devices table makes it easier to store different types of devices together. The role="sensor" tells us that the device is a sensor. This also makes it easier to add other types of devices later.

7. What should happen when the client posts an **unknown** `type`? Where should that rejection be decided (registry/service vs router constructing a concrete class anyway)?

> [!NOTE]
> ***Your Answer***
>
> If the client sends an unknown type, the registry or sensor service should reject it. The router should not try to create a sensor that it does not know about.

## C. Compare, contrast, and scenarios

8. Contrast Factory Method with a **simple factory** (one function full of `if type == ...`). When is the simple factory “good enough,” and why does this phase still want polymorphic creators?

> [!NOTE]
> ***Your Answer***
>
> A simple factory is one function that uses if/elif to decide which sensor to create. It can be fine for a small application. This phase uses Factory Method because it makes adding new sensor types easier and keeps the creation logic separated.

9. Contrast Factory Method with **Abstract Factory** (Phase 3). Factory Method answers which question? Abstract Factory answers which different question? Why is Factory Method enough for Phase 2 sensors?

> [!NOTE]
> ***Your Answer***
>
> Factory Method is mainly about which product to create. Abstract Factory is about creating a group of related products. Factory Method is enough for Phase 2 because we only need to create different sensor types.

10. A classmate puts SQLAlchemy session commits (or FastAPI request parsing) **inside** a concrete creator. Why is that a trap? Where should persistence and HTTP stay instead?

> [!NOTE]
> ***Your Answer***
>
> Putting database commits or FastAPI code inside a creator mixes different responsibilities. The creator should only handle creating the sensor. The router should handle HTTP, and the service or repository should handle database operations.
