# Phase 4 — Builder questions

**Pattern / focus:** Builder.

**Read first:** [Guide 04](../../materials/guides/04-builder.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example ramen orders) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to locations, zones, `location_id`, and the configuration wizard from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Builder in plain language. Why does construction of a complex object need **stepwise assembly** and **validation at the end** (`build()`), instead of a telescoping constructor or a half-filled dict written straight to the database?

> [!NOTE]
> **_Your Answer_**
>
> Builder lets us create a complex object step by step and keep the construction process organized. In this project, we can set the location name and add zones before creating the final configuration. The build() method checks that the complete configuration is valid before it is used. This is safer than a large constructor or saving a half-filled dictionary because invalid or incomplete data should never reach the database.

2. Name the main participants (**product**, **builder**, **optional director**, **client**). Until `build()` succeeds, is the intermediate object a finished domain product? Why does that distinction matter?

> [!NOTE]
> **_Your Answer_**
>
> Product: LocationConfig, containing a Location and its zones.
Builder: LocationConfigBuilder, which collects the location name and zones and validates them.
Director: Not required in this implementation because the client controls the construction steps directly.
Client: The application service/mapper that uses the builder.

Until build() succeeds, the configuration is only being assembled inside the builder. It is not a finished domain product. This matters because only a valid completed configuration should be passed to the repository for persistence.

3. List at least three kinds of invalid configuration a location/zone `build()` should reject in **this** lab (name, zones, moisture thresholds). Why must those rules live in the **domain** builder, not only in the HTTP layer?

> [!NOTE]
> **_Your Answer_**
>
> The builder should reject an empty location name, a location with no zones, an empty zone name, duplicate zone names, and invalid moisture thresholds. The low threshold must be lower than the high threshold, and both values must be between 0.0 and 1.0.

These rules belong in the domain builder because the domain should protect itself regardless of where the request comes from. If validation only exists in FastAPI, another part of the application could create invalid configurations without going through the HTTP layer.

## B. This phase of the application

4. What aggregate does the builder produce (location plus zones)? Why does this course use **`location_id`** (and never `greenhouse_id`) as the name for that scope?

> [!NOTE]
> **_Your Answer_**
>
> The builder produces a LocationConfig, which contains one Location and its collection of Zone objects. Each zone belongs to the location through location_id.

This project uses location_id because the required scope is called a location. The application should use the same name consistently, so greenhouse_id should not be introduced as another name for the same concept.

5. Describe the path from API request to persistence: DTO → builder steps → `build()` → repository. What must **not** be persisted if `build()` raises `ConfigurationError` (or equivalent)? Why does assigning a device wait until the zone row exists, and why does the client send only `zone_id`?

> [!NOTE]
> **_Your Answer_**
>
> The API receives a LocationConfigRequest DTO. The mapper passes the location name and each zone to LocationConfigBuilder. The builder validates the values and build() creates the final LocationConfig. The repository then saves the location and its zones to PostgreSQL.

If build() raises ConfigurationError, nothing from that configuration should be persisted. A device assignment waits until the zone exists because the device needs a real zone_id to reference. The client only sends zone_id because the backend can get the zone's location_id from the database, which prevents the client from sending conflicting location information.

6. Saving a location and its zones must be **one transaction**. What goes wrong if the location row commits and a later zone insert fails? How does that relate to “no half-built aggregates in the database”?

> [!NOTE]
> **_Your Answer_**
>
> If the location is committed first and a later zone insert fails, the database could contain a location without all the zones that were supposed to belong to it. This would leave a partially built configuration in the database. Using one transaction means the location and all its zones are saved together. If something fails, the transaction can be rolled back, so the database does not contain a half-built aggregate.

7. The configuration wizard UI collects fields in steps. How does that UI map to Builder without turning React (or the HTTP handler) into the place that owns domain validation?

> [!NOTE]
> **_Your Answer_**
>
> The React wizard collects the location and zone information and sends it to the API as a DTO. The mapper then uses LocationConfigBuilder to build and validate the configuration. React handles the UI, while the domain builder handles the actual business rules.

## C. Compare, contrast, and scenarios

8. Contrast Builder with Factory Method and with Abstract Factory. Which pattern answers “which type?”, which answers “which matching kit?”, and which answers “how do we assemble one **valid whole** in steps?”

> [!NOTE]
> **_Your Answer_**
>
> Factory Method answers “which type should I create?” For example, choosing which sensor implementation to create.

Abstract Factory answers “which matching kit or family should I create?” For example, creating a compatible group of greenhouse devices from the same family.

Builder answers “how do I assemble one valid whole step by step?” In this phase, it builds a complete location configuration with its zones and validates it before saving.

9. Fluent method chaining (`builder.add_zone(...).build()`) is a coding style. Why is a fluent interface **not** the same thing as the Builder pattern?

> [!NOTE]
> **_Your Answer_**
>
> Fluent chaining is just a way of calling methods by returning self. It does not automatically make a class a Builder. Builder is about step-by-step construction of a complex object and producing a valid final product.

10. A classmate validates thresholds only in FastAPI / Pydantic and leaves `build()` empty. Another mutates builder fields after `build()` while treating the product as immutable. Explain why each is a trap.

> [!NOTE]
> **_Your Answer_**
>
> The first approach is a problem because the domain builder does not protect the business rules. Another part of the application could bypass FastAPI and create an invalid configuration. Validation should therefore also be enforced by the domain builder.

The second approach is a problem because after build() the returned domain product should represent a completed configuration. If the builder or its data can change it afterwards, the product is no longer reliably immutable. The builder should be used to finish the configuration first, and then the resulting domain object should remain unchanged.
