import { useEffect, useState } from "react";
import {
  createSensor,
  fetchSensors,
  type SensorDto,
} from "../../services/api";

export default function SensorList() {
  const [sensors, setSensors] = useState<SensorDto[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function loadSensors() {
    try {
      setError(null);
      const data = await fetchSensors();
      // Show newest created sensors first
      setSensors([...data].reverse());
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

  async function handleCreateSensor(type: "moisture" | "light") {
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

  useEffect(() => {
    loadSensors();
  }, []);

  return (
    <section className="max-w-4xl mx-auto py-4">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex gap-3">
          <button
            type="button"
            disabled={isSubmitting}
            onClick={() => handleCreateSensor("moisture")}
            className="rounded bg-green-600 px-4 py-2 font-medium text-white hover:bg-green-700 disabled:opacity-50"
          >
            {isSubmitting ? "Adding..." : "+ Add Moisture Sensor"}
          </button>

          <button
            type="button"
            disabled={isSubmitting}
            onClick={() => handleCreateSensor("light")}
            className="rounded bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {isSubmitting ? "Adding..." : "+ Add Light Sensor"}
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
        <div className="space-y-3">
          {sensors.map((sensor) => (
            <div
              key={sensor.id}
              className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
            >
              <div className="flex items-center justify-between mb-1">
                <h3 className="font-semibold text-gray-800">
                  {sensor.display_name || "Unnamed sensor"}
                </h3>
                <span className="text-xs font-mono text-gray-400">
                  {String(sensor.id).slice(0, 8)}...
                </span>
              </div>

              <p className="text-xs font-medium text-gray-500 mb-2">
                Type: <span className="font-mono text-gray-700">{sensor.device_type}</span>
              </p>

              <pre className="overflow-x-auto rounded bg-gray-50 p-2 text-xs text-gray-700 border border-gray-100">
                {JSON.stringify(sensor.default_config, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
