export type DeviceFamily = "simulation" | "edge";
export type DeviceRole = "sensor" | "actuator";

export interface SensorDto {
  id: string;
  device_type: string;
  display_name: string;
  default_config: Record<string, unknown>;
  created_at?: string;
}

export interface DeviceDto {
  id: string;
  device_type: string;
  role: DeviceRole;
  device_family: DeviceFamily;
  display_name: string;
  default_config: Record<string, unknown>;
  created_at?: string;
}

export interface ReadingDto {
  device_id: string;
  value: number;
  unit: string;
  source: string;
  recorded_at: string;
}

export interface SamplingDto {
  device_id: string;
  sampling_interval_seconds: number;
  tracking_enabled: boolean;
}

const API_BASE = "/api";

export async function fetchHealth(): Promise<{ status: string }> {
  const res = await fetch("/health");

  if (!res.ok) {
    throw new Error("Health check failed");
  }

  return res.json();
}

export async function fetchSensors(): Promise<SensorDto[]> {
  const res = await fetch(`${API_BASE}/sensors`);

  if (!res.ok) {
    throw new Error("Failed to fetch sensors");
  }

  return res.json();
}

export async function createSensor(
  type: string,
  display_name: string
): Promise<SensorDto> {
  const res = await fetch(`${API_BASE}/sensors`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type,
      display_name,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));

    throw new Error(
      errorData.detail || "Failed to create sensor"
    );
  }

  return res.json();
}

export async function fetchDevices(
  family?: DeviceFamily,
  role?: DeviceRole
): Promise<DeviceDto[]> {
  const params = new URLSearchParams();

  if (family) {
    params.append("family", family);
  }

  if (role) {
    params.append("role", role);
  }

  const query = params.toString()
    ? `?${params.toString()}`
    : "";

  const res = await fetch(`${API_BASE}/devices${query}`);

  if (!res.ok) {
    throw new Error("Failed to fetch devices");
  }

  return res.json();
}

export async function provisionDeviceKit(
  family: DeviceFamily
): Promise<DeviceDto[]> {
  const res = await fetch(
    `${API_BASE}/devices/provision?family=${family}`,
    {
      method: "POST",
    }
  );

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));

    throw new Error(
      errorData.detail || "Failed to provision kit"
    );
  }

  return res.json();
}

export async function readSensor(
  sensorId: string
): Promise<ReadingDto> {
  const res = await fetch(
    `${API_BASE}/sensors/${sensorId}/read`,
    {
      method: "POST",
    }
  );

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));

    throw new Error(
      errorData.detail || "Failed to read sensor"
    );
  }

  return res.json();
}

export async function fetchSensorReadings(
  sensorId: string,
  limit = 1
): Promise<ReadingDto[]> {
  const res = await fetch(
    `${API_BASE}/sensors/${sensorId}/readings?limit=${limit}`
  );

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));

    throw new Error(
      errorData.detail || "Failed to fetch sensor readings"
    );
  }

  return res.json();
}

export async function updateDeviceSampling(
  deviceId: string,
  sampling_interval_seconds: number,
  tracking_enabled: boolean
): Promise<SamplingDto> {
  const res = await fetch(
    `${API_BASE}/devices/${deviceId}/sampling`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sampling_interval_seconds,
        tracking_enabled,
      }),
    }
  );

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));

    throw new Error(
      errorData.detail ||
        "Failed to update sampling settings"
    );
  }

  return res.json();
}