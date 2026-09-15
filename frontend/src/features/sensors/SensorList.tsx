```tsx
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

  async function loadSensors() {
    try {
      setError(null);

      const data = await fetchSensors();
      setSensors(data);
    } catch (error) {
      console.error("Failed to load sensors:", error);

      if (error instanceof Error) {
        setError(`Failed to load sensors: ${error.message}`);
      } else {
        setError("Failed to load sensors.");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateSensor(type: "moisture" | "light") {
    try {
      setError(null);

      const displayName =
        type === "moisture"
          ? "New moisture sensor"
          : "New light sensor";

      await createSensor(type, displayName);

      await loadSensors();
    } catch (error) {
      console.error("Failed to create sensor:", error);

      if (error instanceof Error) {
        setError(`Failed to create sensor: ${error.message}`);
      } else {
        setError("Failed to create sensor.");
      }
    }
  }

  useEffect(() => {
    loadSensors();
  }, []);

  return (
    <section>
      <div className="mb-4 flex gap-3">
        <button
          type="button"
          onClick={() => handleCreateSensor("moisture")}
          className="rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700"
        >
          Add Moisture Sensor
        </button>

        <button
          type="button"
          onClick={() => handleCreateSensor("light")}
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          Add Light Sensor
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded border border-red-300 bg-red-50 p-3 text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <p>Loading sensors...</p>
      ) : sensors.length === 0 ? (
        <p>No sensors found.</p>
      ) : (
        <div className="space-y-3">
          {sensors.map((sensor) => (
            <div key={sensor.id} className="rounded border p-4">
              <h3 className="font-semibold">
                {sensor.display_name || "Unnamed sensor"}
              </h3>

              <p className="text-sm text-gray-600">
                Type: {sensor.device_type}
              </p>

              <pre className="mt-2 overflow-x-auto rounded bg-gray-100 p-2 text-sm">
                {JSON.stringify(sensor.default_config, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
```
