# Builder Pattern — Smart Greenhouse

## 1. Purpose

The Builder pattern is used in the Smart Greenhouse application to create a valid location configuration step by step.

A location configuration contains:

- A location name
- One or more zones
- Moisture thresholds for each zone
- An optional watering schedule for each zone

The Builder keeps the construction and validation of the configuration inside the domain layer before the configuration is saved to PostgreSQL.

---

## 2. Why Builder is used here

A location configuration contains several related values and validation rules.

For example, a valid configuration must:

- Have a non-empty location name
- Contain at least one zone
- Have unique zone names
- Have moisture thresholds between `0.0` and `1.0`
- Have the low threshold smaller than the high threshold

Creating the configuration directly in the API or database layer would mix construction and validation with infrastructure code.

The Builder provides a clear step-by-step way to construct the configuration and validate it before persistence.

---

## 3. Main Builder class

The Builder is implemented in:

`backend/src/domain/locations/config_builder.py`

The main class is:

`LocationConfigBuilder`

It provides three main operations:

```text
with_location_name(...)
        ↓
add_zone(...)
        ↓
build()