import { useEffect, useState } from "react";
import {
  createSensor,
  fetchSensorReadings,
  fetchSensors,
  readSensor,
  updateDeviceSampling,
  type ReadingDto,
  type SensorDto,
} from "../../services/api";

type SensorSettings = {
  sampling_interval_seconds: number;
  tracking_enabled: boolean;
};

export default function SensorList() {
  const [sensors, setSensors] = useState<SensorDto[]>([]);
  const [readings, setReadings] = useState<
    Record<string, ReadingDto | null>
  >({});
  const [settings, setSettings] = useState<
    Record<string, SensorSettings>
  >({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [readingSensorId, setReadingSensorId] = useState<string | null>(
    null
  );
  const [savingSensorId, setSavingSensorId] = useState<string | null>(
    null
  );

  async function loadSensors() {
    try {
      setError(null);

      const data = await fetchSensors();

      // Show newest created sensors first.
      const orderedSensors = [...data].reverse();

      setSensors(orderedSensors);

      const initialSettings: Record<string, SensorSettings> = {};

      orderedSensors.forEach((sensor) => {
        const config = sensor.default_config;

        const samplingInterval =
          typeof config.sampling_interval_seconds === "number"
            ? config.sampling_interval_seconds
            : 300;

        const trackingEnabled =
          typeof config.tracking_enabled === "boolean"
            ? config.tracking_enabled
            : true;

        initialSettings[String(sensor.id)] = {
          sampling_interval_seconds: samplingInterval,
          tracking_enabled: trackingEnabled,
        };
      });

      setSettings((current) => ({
        ...initialSettings,
        ...current,
      }));

      await loadLatestReadings(orderedSensors);
    } catch (err: unknown) {
      console.error("Failed to load sensors:", err);

      if (err instanceof Error) {
        setError("Failed to load sensors: " + err.message);
      } else {
        setError("Failed to load sensors.");
      }
    } finally {
      setLoading(false);
    }
  }

  async function loadLatestReadings(
    sensorList: SensorDto[] = sensors
  ) {
    const results = await Promise.all(
      sensorList.map(async (sensor) => {
        try {
          const sensorReadings = await fetchSensorReadings(
            String(sensor.id),
            1
          );

          return {
            id: String(sensor.id),
            reading: sensorReadings[0] ?? null,
          };
        } catch (err) {
          console.error(
            `Failed to load reading for sensor ${sensor.id}:`,
            err
          );

          return {
            id: String(sensor.id),
            reading: null,
          };
        }
      })
    );

    setReadings((current) => {
      const next = { ...current };

      results.forEach(({ id, reading }) => {
        next[id] = reading;
      });

      return next;
    });
  }

  async function handleCreateSensor(
    type: "moisture" | "light"
  ) {
    try {
      setIsSubmitting(true);
      setError(null);

      const count = sensors.length + 1;

      const displayName =
        type === "moisture"
          ? `Moisture Sensor #${count}`
          : `Light Sensor #${count}`;

      await createSensor(type, displayName);

      await loadSensors();
    } catch (err: unknown) {
      console.error("Failed to create sensor:", err);

      if (err instanceof Error) {
        setError("Failed to create sensor: " + err.message);
      } else {
        setError("Failed to create sensor.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleRead(sensorId: string) {
    try {
      setReadingSensorId(sensorId);
      setError(null);

      const reading = await readSensor(sensorId);

      setReadings((current) => ({
        ...current,
        [sensorId]: reading,
      }));
    } catch (err: unknown) {
      console.error("Failed to read sensor:", err);

      if (err instanceof Error) {
        setError("Failed to read sensor: " + err.message);
      } else {
        setError("Failed to read sensor.");
      }
    } finally {
      setReadingSensorId(null);
    }
  }

  function updateSetting(
    sensorId: string,
    changes: Partial<SensorSettings>
  ) {
    setSettings((current) => ({
      ...current,
      [sensorId]: {
        sampling_interval_seconds:
          current[sensorId]?.sampling_interval_seconds ?? 300,
        tracking_enabled:
          current[sensorId]?.tracking_enabled ?? true,
        ...changes,
      },
    }));
  }

  async function handleSaveSampling(sensorId: string) {
    const sensorSettings = settings[sensorId];

    if (!sensorSettings) {
      return;
    }

    try {
      setSavingSensorId(sensorId);
      setError(null);

      const updated = await updateDeviceSampling(
        sensorId,
        sensorSettings.sampling_interval_seconds,
        sensorSettings.tracking_enabled
      );

      setSettings((current) => ({
        ...current,
        [sensorId]: {
          sampling_interval_seconds:
            updated.sampling_interval_seconds,
          tracking_enabled: updated.tracking_enabled,
        },
      }));
    } catch (err: unknown) {
      console.error(
        "Failed to update sampling settings:",
        err
      );

      if (err instanceof Error) {
        setError(
          "Failed to update sampling settings: " +
            err.message
        );
      } else {
        setError("Failed to update sampling settings.");
      }
    } finally {
      setSavingSensorId(null);
    }
  }

  useEffect(() => {
    loadSensors();
  }, []);

  useEffect(() => {
    if (sensors.length === 0) {
      return;
    }

    const interval = window.setInterval(() => {
      loadLatestReadings(sensors);
    }, 5000);

    return () => {
      window.clearInterval(interval);
    };
  }, [sensors]);

  return (
    <section className="mx-auto max-w-4xl py-4">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex gap-3">
          <button
            type="button"
            disabled={isSubmitting}
            onClick={() => handleCreateSensor("moisture")}
            className="rounded bg-green-600 px-4 py-2 font-medium text-white hover:bg-green-700 disabled:opacity-50"
          >
            {isSubmitting
              ? "Adding..."
              : "+ Add Moisture Sensor"}
          </button>

          <button
            type="button"
            disabled={isSubmitting}
            onClick={() => handleCreateSensor("light")}
            className="rounded bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {isSubmitting
              ? "Adding..."
              : "+ Add Light Sensor"}
          </button>
        </div>

        <span className="text-sm font-semibold text-gray-500">
          Total: {sensors.length} sensors
        </span>
      </div>

      {error && (
        <div className="mb-4 rounded border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <p className="text-gray-500">Loading sensors...</p>
      ) : sensors.length === 0 ? (
        <p className="text-gray-500">No sensors found.</p>
      ) : (
        <div className="space-y-4">
          {sensors.map((sensor) => {
            const sensorId = String(sensor.id);
            const reading = readings[sensorId];

            const sensorSettings = settings[sensorId] ?? {
              sampling_interval_seconds: 300,
              tracking_enabled: true,
            };

            return (
              <div
                key={sensorId}
                className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
              >
                <div className="mb-1 flex items-center justify-between">
                  <h3 className="font-semibold text-gray-800">
                    {sensor.display_name || "Unnamed sensor"}
                  </h3>

                  <span className="font-mono text-xs text-gray-400">
                    {sensorId.slice(0, 8)}...
                  </span>
                </div>

                <p className="mb-4 text-xs font-medium text-gray-500">
                  Type:{" "}
                  <span className="font-mono text-gray-700">
                    {sensor.device_type}
                  </span>
                </p>

                <div className="mb-4 rounded border border-gray-100 bg-gray-50 p-3">
                  <div className="mb-2 flex items-center justify-between">
                    <h4 className="text-sm font-semibold text-gray-700">
                      Latest reading
                    </h4>

                    <button
                      type="button"
                      disabled={readingSensorId === sensorId}
                      onClick={() => handleRead(sensorId)}
                      className="rounded bg-gray-800 px-3 py-1.5 text-xs font-medium text-white hover:bg-gray-700 disabled:opacity-50"
                    >
                      {readingSensorId === sensorId
                        ? "Reading..."
                        : "Read Now"}
                    </button>
                  </div>

                  {reading ? (
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-gray-500">
                          Value:
                        </span>{" "}
                        <span className="font-semibold text-gray-800">
                          {reading.value.toFixed(2)}{" "}
                          {reading.unit}
                        </span>
                      </div>

                      <div>
                        <span className="text-gray-500">
                          Source:
                        </span>{" "}
                        <span className="font-semibold text-gray-800">
                          {reading.source}
                        </span>
                      </div>

                      <div className="col-span-2">
                        <span className="text-gray-500">
                          Recorded:
                        </span>{" "}
                        <span className="text-gray-700">
                          {new Date(
                            reading.recorded_at
                          ).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">
                      No reading recorded yet.
                    </p>
                  )}
                </div>

                <div className="mb-4 rounded border border-gray-100 p-3">
                  <h4 className="mb-3 text-sm font-semibold text-gray-700">
                    Sampling settings
                  </h4>

                  <div className="flex flex-wrap items-end gap-4">
                    <label className="flex flex-col gap-1 text-sm text-gray-600">
                      Interval (seconds)
                      <input
                        type="number"
                        min={5}
                        value={
                          sensorSettings.sampling_interval_seconds
                        }
                        onChange={(event) =>
                          updateSetting(sensorId, {
                            sampling_interval_seconds:
                              Number(event.target.value),
                          })
                        }
                        className="w-36 rounded border border-gray-300 px-3 py-2 text-gray-800"
                      />
                    </label>

                    <label className="flex items-center gap-2 pb-2 text-sm text-gray-600">
                      <input
                        type="checkbox"
                        checked={sensorSettings.tracking_enabled}
                        onChange={(event) =>
                          updateSetting(sensorId, {
                            tracking_enabled:
                              event.target.checked,
                          })
                        }
                        className="h-4 w-4"
                      />
                      Tracking enabled
                    </label>

                    <button
                      type="button"
                      disabled={savingSensorId === sensorId}
                      onClick={() =>
                        handleSaveSampling(sensorId)
                      }
                      className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
                    >
                      {savingSensorId === sensorId
                        ? "Saving..."
                        : "Save settings"}
                    </button>
                  </div>
                </div>

                <details>
                  <summary className="cursor-pointer text-xs font-medium text-gray-500">
                    Device configuration
                  </summary>

                  <pre className="mt-2 overflow-x-auto rounded border border-gray-100 bg-gray-50 p-2 text-xs text-gray-700">
                    {JSON.stringify(
                      sensor.default_config,
                      null,
                      2
                    )}
                  </pre>
                </details>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}