Part A. Pattern

1. What is a design pattern? What is it not?

A design pattern is a common way to solve a software design problem. It gives developers an idea of how to organize the code. It is not ready-made code, and we do not need to use a pattern for every problem.

2. What are the three GoF pattern families?

The three GoF pattern families are:

Creational: Helps with creating objects
Structural: Helps with connecting and organizing classes and objects.
Behavioral: Helps with how objects communicate and work together.

3. When should we skip a pattern?

We should skip a pattern when the problem is simple and normal code is enough. Using a pattern without a real reason can make the code more complicated.

Part B. This phase of the application

4. Why is Phase 1 almost empty?

Phase 1 is mainly about creating the basic project structure. We need to make sure the frontend, backend, database, and migrations can work together before adding the actual greenhouse features.

5. What belongs in the four backend layers?

Domain: Main business rules and concepts.
Application: Application logic and use cases.
Infrastructure: Database and other technical parts.
Interfaces/API: API routes and HTTP-related code.

For example, FastAPI code should not be placed inside the domain layer.

6. What does GET /health return?

The `/health` endpoint checks the backend and PostgreSQL connection. When everything works, it returns a response such as `{"status": "ok", "db": "ok"}`. `/scalar` is used for API documentation, while `/docs` is disabled.

7. Why use Alembic before creating business tables?

Alembic helps us keep track of database changes. Starting with it means that future tables and changes can be managed through migrations instead of changing the database manually.

 Part C. Compare, contrast, and scenarios

 8. What is dependency direction?

The outer layers can depend on the inner layers, but the domain should stay independent. For example, the domain should not depend on FastAPI or SQLAlchemy.

9. Frontend cannot show the health status. What should you check?

First, I would check that both frontend and backend are running. Then I would test the `/health` endpoint. If it works, I would check the API URL, CORS, and frontend configuration.

10. What is still missing after Phase 1?

The actual greenhouse features are still missing. Later phases will add things like sensors, devices, database tables, APIs, business logic, design patterns, and testing.

