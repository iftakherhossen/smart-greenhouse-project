# Phase 3 — Abstract Factory questions

**Pattern / focus:** Abstract Factory.

**Read first:** [Guide 03](../../materials/guides/03-abstract-factory.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example warrior/mage class kits) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to device families, provision, and the unified devices API from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Abstract Factory in plain language. What goes wrong when related products are chosen independently (`if format` for each piece) instead of as a **family**?

> [!NOTE]
> ***Your Answer***
>
> The purpose of Abstract Factory is to create a group of related objects that are designed to work together. If we choose each product separately using different if statements, we can accidentally mix products from different families. Using one factory keeps the whole set consistent.

2. Name the main participants (**abstract factory**, **concrete factory**, **abstract products**, **concrete products**, **client**). How does choosing a factory at the start **commit** the client to one family?

> [!NOTE]
> ***Your Answer***
>
> The main participants are the abstract factory, concrete factories, abstract products, concrete products, and the client. In this application, the abstract factory defines how a device family is created, while the simulation and edge factories create the actual devices. When the client chooses one factory at the beginning, all devices created from it belong to the same family.

3. When should you use Abstract Factory, and when should you skip it (for example only one product type per request, or mixing siblings is valid)?

> [!NOTE]
> ***Your Answer***
>
> Abstract Factory is useful when an application needs several related products that should work together as one family. We should skip it when there is only one product type to create or when mixing different products is valid and does not cause problems. In those cases, a simpler Factory Method or normal constructor can be enough.

## B. This phase of the application

4. In this lab, what is a **device family**, and what does `create_device_set()` (or your equivalent) return? Why must a simulation kit and an edge kit not mix incompatible siblings?

> [!NOTE]
> ***Your Answer***
>
> A device family is a group of devices designed for the same environment, such as the simulation family or the edge family. create_device_set() returns a complete kit of devices, including two sensors and two actuators. The simulation and edge kits should not be mixed because they can have different protocols, labels, and configuration intended for their specific environment.

5. Phase 2 Factory Method creators still exist. How does Abstract Factory **compose** them rather than replace them? What would you lose if you deleted the sensor creators and inlined all construction inside the family factory?

> [!NOTE]
> ***Your Answer***
>
> The Abstract Factory uses the Phase 2 sensor creators to create the individual sensor types and then combines them with the actuators into a complete device family. It does not replace the existing creators. If we deleted the sensor creators and created everything directly inside the family factory, we would lose the separation provided by the Factory Method pattern and make the family factory responsible for too much individual sensor construction.

6. Why add a `device_family` column on the existing `devices` table (with a default/backfill such as `"simulation"`) instead of a new table per family? What happens to Phase 2 sensor rows if you forget the backfill?

> [!NOTE]
> ***Your Answer***
>
> The device_family column lets us store the family of every device while continuing to use the existing devices table. Creating separate tables for each family would make the database more complicated and duplicate the same device structure. The default or backfill value of "simulation" also keeps existing Phase 2 sensor rows valid. If we forget the backfill, existing rows could have a missing family value and would not be consistent with the new model.

7. `POST /api/devices/provision` returns a kit (expected size: two sensors and two actuators). `GET /api/devices` can filter by `family` and `role`. Why must the UI be able to filter by family? Why do `/api/sensors` routes from Phase 2 still need to work?

> [!NOTE]
> ***Your Answer***
>
> The UI needs to filter by family so that users can view the devices belonging to the selected simulation or edge kit instead of mixing devices from different families. The /api/sensors routes must still work because Phase 3 builds on Phase 2 and should not break the existing sensor functionality. The Phase 2 Factory Method functionality is still part of the application.

## C. Compare, contrast, and scenarios

8. Draw the contrast in one paragraph: Factory Method vs Abstract Factory. Use the questions “which **one** product?” versus “which product **line**?” and mention that Abstract Factory often **uses** Factory Method–style methods inside.

> [!NOTE]
> ***Your Answer***
>
> Factory Method focuses on deciding which one product to create, such as creating a specific type of sensor. Abstract Factory focuses on deciding which product line to create, such as a complete simulation or edge device family containing sensors and actuators. In this phase, the Abstract Factory can use the Factory Method sensor creators internally to create the individual sensors and then combine them into a complete family.

9. A DTO or HTTP handler constructs concrete simulation/edge device types directly, bypassing the family factory. What consistency bug can that reintroduce? How should HTTP stay on the abstract factory / service instead?

> [!NOTE]
> ***Your Answer***
>
> If the DTO or HTTP handler creates simulation or edge devices directly, it could accidentally create a mixed kit, for example a simulation sensor with an edge actuator. This would break the consistency that the Abstract Factory is supposed to provide. The HTTP layer should call the service, and the service should choose the correct family factory and provision the complete device set.

10. Someone proposes a single “god factory” that creates locations, readings, and devices “because we already have a factory.” Why is that a misuse of Abstract Factory?

> [!NOTE]
> ***Your Answer***
>
> A single factory for locations, readings, and devices would mix unrelated responsibilities. Abstract Factory is meant to create a family of related products, not every object in the whole application. Locations, readings, and devices have different responsibilities and patterns, so each part should have its own appropriate design instead of putting everything into one large factory.
