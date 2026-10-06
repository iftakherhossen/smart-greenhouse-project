import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from src.application.sensors.reading_ingest import ReadingIngest
from src.application.sensors.simulation_sampler import SimulationSampler
from src.infrastructure.db import SessionLocal
from src.infrastructure.persistence.device_repository import DeviceRepository
from src.infrastructure.persistence.sensor_reading_repository import (
    SensorReadingRepository,
)
from src.interfaces.api.devices import router as devices_router
from src.interfaces.api.health import router as health_router
from src.interfaces.api.locations import router as locations_router
from src.interfaces.api.sensors import router as sensors_router


async def simulation_sampler_loop(
    sampler: SimulationSampler,
) -> None:
    while True:
        db = SessionLocal()

        try:
            device_repository = DeviceRepository(db)
            reading_repository = SensorReadingRepository(db)

            reading_ingest = ReadingIngest(
                device_repository=device_repository,
                reading_repository=reading_repository,
            )

            sampler._device_repository = device_repository
            sampler._reading_ingest = reading_ingest

            sampler.run_once()

        except Exception as error:
            print(f"Simulation sampler error: {error}")

        finally:
            db.close()

        await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()

    try:
        device_repository = DeviceRepository(db)
        reading_repository = SensorReadingRepository(db)

        reading_ingest = ReadingIngest(
            device_repository=device_repository,
            reading_repository=reading_repository,
        )

        sampler = SimulationSampler(
            device_repository=device_repository,
            reading_ingest=reading_ingest,
        )
    finally:
        db.close()

    sampler_task = asyncio.create_task(
        simulation_sampler_loop(sampler)
    )

    try:
        yield
    finally:
        sampler_task.cancel()

        try:
            await sampler_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Smart Greenhouse API",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(sensors_router)
app.include_router(devices_router)
app.include_router(locations_router)


@app.get("/")
def root():
    return {
        "message": "Smart Greenhouse API",
        "status": "ok",
    }


@app.get("/scalar", include_in_schema=False)
def scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )