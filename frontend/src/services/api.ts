const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface SensorDto {
  id: string;
  device_type: string;
  display_name: string | null;
  default_config: Record<string, unknown>;
}

export async function fetchSensors(): Promise<SensorDto[]> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`);

  if (!response.ok) {
    throw new Error("Failed to fetch sensors");
  }

  return response.json();
}

export async function createSensor(
  type: "moisture" | "light",
  displayName?: string,
): Promise<SensorDto> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type,
      display_name: displayName || null,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to create sensor");
  }

  return response.json();
}