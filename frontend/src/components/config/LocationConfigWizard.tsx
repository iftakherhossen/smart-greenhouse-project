import { useEffect, useMemo, useState } from "react";

type Zone = {
  id: string;
  location_id: string;
  name: string;
  moisture_threshold_low: number;
  moisture_threshold_high: number;
  schedule: Record<string, unknown>;
};

type Location = {
  id: string;
  name: string;
};

type LocationConfig = {
  location: Location;
  zones: Zone[];
};

type Device = {
  id: string;
  device_type: string;
  role: "sensor" | "actuator";
  device_family: string;
  display_name: string;
  default_config: Record<string, unknown>;
  zone_id: string | null;
  location_id: string | null;
};

type DraftZone = {
  name: string;
  low: string;
  high: string;
};

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function apiRequest<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const error = await response.json();

      if (typeof error.detail === "string") {
        message = error.detail;
      } else if (Array.isArray(error.detail)) {
        message = error.detail
          .map((item: { msg?: string }) => item.msg ?? "Invalid request")
          .join(", ");
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export function LocationConfigWizard() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocationId, setSelectedLocationId] = useState<string>("");

  const [locationName, setLocationName] = useState("");
  const [zones, setZones] = useState<Zone[]>([]);

  const [draftZones, setDraftZones] = useState<DraftZone[]>([
    {
      name: "Zone A",
      low: "0.3",
      high: "0.7",
    },
  ]);

  const [newZoneName, setNewZoneName] = useState("");
  const [newLow, setNewLow] = useState("0.3");
  const [newHigh, setNewHigh] = useState("0.7");

  const [editingZoneId, setEditingZoneId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState("");
  const [editingLow, setEditingLow] = useState("");
  const [editingHigh, setEditingHigh] = useState("");

  const [devices, setDevices] = useState<Device[]>([]);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const selectedLocation = useMemo(
    () =>
      locations.find(
        (location) => location.id === selectedLocationId,
      ) ?? null,
    [locations, selectedLocationId],
  );

  const allZones = useMemo(
    () =>
      locations.flatMap((location) =>
        location.id === selectedLocationId ? zones : [],
      ),
    [locations, selectedLocationId, zones],
  );

  async function loadLocations() {
    const data = await apiRequest<Location[]>("/api/locations");
    setLocations(data);
  }

  async function loadLocation(locationId: string) {
    const data = await apiRequest<LocationConfig>(
      `/api/locations/${locationId}/config`,
    );

    setLocationName(data.location.name);
    setZones(data.zones);
  }

  async function loadDevices() {
    const data = await apiRequest<Device[]>("/api/devices");
    setDevices(data);
  }

  useEffect(() => {
    async function initialize() {
      try {
        setLoading(true);
        setError("");

        const locationData = await apiRequest<Location[]>(
          "/api/locations",
        );

        setLocations(locationData);

        if (locationData.length > 0) {
          const firstLocation = locationData[0];

          setSelectedLocationId(firstLocation.id);

          const config = await apiRequest<LocationConfig>(
            `/api/locations/${firstLocation.id}/config`,
          );

          setLocationName(config.location.name);
          setZones(config.zones);
        }

        await loadDevices();
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load configuration.",
        );
      } finally {
        setLoading(false);
      }
    }

    initialize();
  }, []);

  async function selectLocation(locationId: string) {
    try {
      setError("");
      setMessage("");
      setLoading(true);

      setSelectedLocationId(locationId);

      await loadLocation(locationId);
      await loadDevices();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load location.",
      );
    } finally {
      setLoading(false);
    }
  }

  function startNewLocation() {
    setSelectedLocationId("");
    setLocationName("");
    setZones([]);

    setDraftZones([
      {
        name: "Zone A",
        low: "0.3",
        high: "0.7",
      },
    ]);

    setError("");
    setMessage("");
  }

  function updateDraftZone(
    index: number,
    field: keyof DraftZone,
    value: string,
  ) {
    setDraftZones((current) =>
      current.map((zone, zoneIndex) =>
        zoneIndex === index
          ? {
              ...zone,
              [field]: value,
            }
          : zone,
      ),
    );
  }

  function addDraftZone() {
    setDraftZones((current) => [
      ...current,
      {
        name: `Zone ${String.fromCharCode(65 + current.length)}`,
        low: "0.3",
        high: "0.7",
      },
    ]);
  }

  function removeDraftZone(index: number) {
    if (draftZones.length <= 1) {
      setError("A location must have at least one zone.");
      return;
    }

    setDraftZones((current) =>
      current.filter((_, zoneIndex) => zoneIndex !== index),
    );
  }

  async function createLocation() {
    try {
      setError("");
      setMessage("");

      if (!locationName.trim()) {
        setError("Location name is required.");
        return;
      }

      if (draftZones.length === 0) {
        setError("At least one zone is required.");
        return;
      }

      setLoading(true);

      const requestZones = draftZones.map((zone) => ({
        name: zone.name.trim(),
        moisture_threshold_low: Number(zone.low),
        moisture_threshold_high: Number(zone.high),
        schedule: {},
      }));

      const data = await apiRequest<LocationConfig>(
        "/api/locations/config",
        {
          method: "POST",
          body: JSON.stringify({
            location_name: locationName.trim(),
            zones: requestZones,
          }),
        },
      );

      await loadLocations();

      setSelectedLocationId(data.location.id);
      setLocationName(data.location.name);
      setZones(data.zones);
      setDraftZones([]);

      setMessage("Location created successfully.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create location.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function deleteLocation() {
    if (!selectedLocationId) {
      return;
    }

    const confirmed = window.confirm(
      `Delete "${selectedLocation?.name ?? "this location"}"?`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setMessage("");
      setLoading(true);

      await apiRequest<void>(
        `/api/locations/${selectedLocationId}`,
        {
          method: "DELETE",
        },
      );

      const remaining = locations.filter(
        (location) => location.id !== selectedLocationId,
      );

      setLocations(remaining);

      if (remaining.length > 0) {
        await selectLocation(remaining[0].id);
      } else {
        startNewLocation();
      }

      setMessage("Location deleted successfully.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete location.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function addZone() {
    if (!selectedLocationId) {
      return;
    }

    try {
      setError("");
      setMessage("");
      setLoading(true);

      const zone = await apiRequest<Zone>(
        `/api/locations/${selectedLocationId}/zones`,
        {
          method: "POST",
          body: JSON.stringify({
            name: newZoneName,
            moisture_threshold_low: Number(newLow),
            moisture_threshold_high: Number(newHigh),
            schedule: {},
          }),
        },
      );

      setZones((current) => [...current, zone]);

      setNewZoneName("");
      setNewLow("0.3");
      setNewHigh("0.7");

      setMessage("Zone added successfully.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to add zone.",
      );
    } finally {
      setLoading(false);
    }
  }

  function startEditing(zone: Zone) {
    setEditingZoneId(zone.id);
    setEditingName(zone.name);
    setEditingLow(String(zone.moisture_threshold_low));
    setEditingHigh(String(zone.moisture_threshold_high));
    setError("");
    setMessage("");
  }

  function cancelEditing() {
    setEditingZoneId(null);
    setEditingName("");
    setEditingLow("");
    setEditingHigh("");
  }

  async function saveZone(zoneId: string) {
    if (!selectedLocationId) {
      return;
    }

    try {
      setError("");
      setMessage("");
      setLoading(true);

      const updated = await apiRequest<Zone>(
        `/api/locations/${selectedLocationId}/zones/${zoneId}`,
        {
          method: "PATCH",
          body: JSON.stringify({
            name: editingName,
            moisture_threshold_low: Number(editingLow),
            moisture_threshold_high: Number(editingHigh),
            schedule: {},
          }),
        },
      );

      setZones((current) =>
        current.map((zone) =>
          zone.id === zoneId ? updated : zone,
        ),
      );

      cancelEditing();
      setMessage("Zone updated successfully.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update zone.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function deleteZone(zoneId: string) {
    if (!selectedLocationId) {
      return;
    }

    const zone = zones.find((item) => item.id === zoneId);

    const confirmed = window.confirm(
      `Delete "${zone?.name ?? "this zone"}"?`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setMessage("");
      setLoading(true);

      await apiRequest<void>(
        `/api/locations/${selectedLocationId}/zones/${zoneId}`,
        {
          method: "DELETE",
        },
      );

      setZones((current) =>
        current.filter((item) => item.id !== zoneId),
      );

      setMessage("Zone deleted successfully.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete zone.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function assignDevice(
    deviceId: string,
    zoneId: string,
  ) {
    try {
      setError("");
      setMessage("");

      await apiRequest(
        `/api/devices/${deviceId}/zone`,
        {
          method: "PUT",
          body: JSON.stringify({
            zone_id: zoneId || null,
          }),
        },
      );

      await loadDevices();

      setMessage("Device assignment updated.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to assign device.",
      );
    }
  }

  const zoneOptions = allZones;

  return (
    <div className="space-y-8">
      {error && (
        <div className="rounded-lg border border-red-800 bg-red-950 px-4 py-3 text-sm text-red-200">
          {error}
        </div>
      )}

      {message && (
        <div className="rounded-lg border border-green-800 bg-green-950 px-4 py-3 text-sm text-green-200">
          {message}
        </div>
      )}

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h3 className="text-xl font-semibold">
              Saved Locations
            </h3>

            <p className="mt-1 text-sm text-slate-400">
              Select a saved location or create a new configuration.
            </p>
          </div>

          <button
            type="button"
            onClick={startNewLocation}
            className="rounded-lg bg-slate-700 px-4 py-2 text-sm font-medium transition hover:bg-slate-600"
          >
            New Location
          </button>
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          {locations.length === 0 && (
            <p className="text-sm text-slate-500">
              No saved locations yet.
            </p>
          )}

          {locations.map((location) => (
            <button
              key={location.id}
              type="button"
              onClick={() => selectLocation(location.id)}
              className={`rounded-lg px-4 py-2 text-sm transition ${
                selectedLocationId === location.id
                  ? "bg-slate-100 text-slate-900"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              }`}
            >
              {location.name}
            </button>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h3 className="text-xl font-semibold">
              Location Configuration
            </h3>

            <p className="mt-1 text-sm text-slate-400">
              Build a location with one or more moisture zones.
            </p>
          </div>

          {selectedLocationId && (
            <button
              type="button"
              onClick={deleteLocation}
              className="rounded-lg border border-red-800 px-4 py-2 text-sm text-red-300 transition hover:bg-red-950"
            >
              Delete Location
            </button>
          )}
        </div>

        <div className="mt-6">
          <label className="mb-2 block text-sm font-medium text-slate-300">
            Location name
          </label>

          <input
            value={locationName}
            onChange={(event) =>
              setLocationName(event.target.value)
            }
            disabled={Boolean(selectedLocationId)}
            placeholder="e.g. Main Greenhouse"
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 text-white outline-none focus:border-slate-500 disabled:cursor-not-allowed disabled:opacity-60"
          />

          {!selectedLocationId && (
            <>
              <div className="mt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold">
                      New Location Zones
                    </h4>

                    <p className="mt-1 text-sm text-slate-400">
                      Add all zones before creating the location.
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={addDraftZone}
                    className="rounded-lg bg-slate-700 px-3 py-2 text-sm text-slate-200 transition hover:bg-slate-600"
                  >
                    + Add Zone
                  </button>
                </div>

                <div className="mt-4 space-y-4">
                  {draftZones.map((zone, index) => (
                    <div
                      key={index}
                      className="rounded-xl border border-slate-800 bg-slate-950 p-5"
                    >
                      <div className="flex items-center justify-between">
                        <h5 className="font-medium">
                          Zone {index + 1}
                        </h5>

                        {draftZones.length > 1 && (
                          <button
                            type="button"
                            onClick={() =>
                              removeDraftZone(index)
                            }
                            className="text-sm text-red-300 hover:text-red-200"
                          >
                            Remove
                          </button>
                        )}
                      </div>

                      <div className="mt-4 grid gap-4 md:grid-cols-3">
                        <input
                          value={zone.name}
                          onChange={(event) =>
                            updateDraftZone(
                              index,
                              "name",
                              event.target.value,
                            )
                          }
                          placeholder="Zone name"
                          className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-white outline-none focus:border-slate-500"
                        />

                        <input
                          type="number"
                          min="0"
                          max="1"
                          step="0.01"
                          value={zone.low}
                          onChange={(event) =>
                            updateDraftZone(
                              index,
                              "low",
                              event.target.value,
                            )
                          }
                          placeholder="Low threshold"
                          className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-white outline-none focus:border-slate-500"
                        />

                        <input
                          type="number"
                          min="0"
                          max="1"
                          step="0.01"
                          value={zone.high}
                          onChange={(event) =>
                            updateDraftZone(
                              index,
                              "high",
                              event.target.value,
                            )
                          }
                          placeholder="High threshold"
                          className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-white outline-none focus:border-slate-500"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <button
                type="button"
                onClick={createLocation}
                disabled={
                  loading ||
                  !locationName.trim() ||
                  draftZones.length === 0
                }
                className="mt-6 rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
              >
                Create Location
              </button>
            </>
          )}
        </div>

        {selectedLocationId && (
          <div className="mt-4 rounded-lg bg-slate-950 px-4 py-3 text-sm">
            <span className="text-slate-500">
              Location ID:
            </span>{" "}
            <span className="font-mono text-slate-300">
              {selectedLocationId}
            </span>
          </div>
        )}
      </section>

      {selectedLocationId && (
        <>
          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div>
              <h3 className="text-xl font-semibold">
                Zones
              </h3>

              <p className="mt-1 text-sm text-slate-400">
                Manage moisture thresholds for this location.
              </p>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <input
                value={newZoneName}
                onChange={(event) =>
                  setNewZoneName(event.target.value)
                }
                placeholder="Zone name"
                className="rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 text-white outline-none focus:border-slate-500"
              />

              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={newLow}
                onChange={(event) =>
                  setNewLow(event.target.value)
                }
                placeholder="Low threshold"
                className="rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 text-white outline-none focus:border-slate-500"
              />

              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={newHigh}
                onChange={(event) =>
                  setNewHigh(event.target.value)
                }
                placeholder="High threshold"
                className="rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 text-white outline-none focus:border-slate-500"
              />
            </div>

            <button
              type="button"
              onClick={addZone}
              disabled={
                loading ||
                !newZoneName.trim()
              }
              className="mt-4 rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              Add Zone
            </button>

            <div className="mt-6 space-y-4">
              {zones.map((zone) => (
                <div
                  key={zone.id}
                  className="rounded-xl border border-slate-800 bg-slate-950 p-5"
                >
                  {editingZoneId === zone.id ? (
                    <div className="space-y-4">
                      <input
                        value={editingName}
                        onChange={(event) =>
                          setEditingName(event.target.value)
                        }
                        className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-white"
                      />

                      <div className="grid gap-4 md:grid-cols-2">
                        <input
                          type="number"
                          min="0"
                          max="1"
                          step="0.01"
                          value={editingLow}
                          onChange={(event) =>
                            setEditingLow(event.target.value)
                          }
                          className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-white"
                        />

                        <input
                          type="number"
                          min="0"
                          max="1"
                          step="0.01"
                          value={editingHigh}
                          onChange={(event) =>
                            setEditingHigh(event.target.value)
                          }
                          className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-white"
                        />
                      </div>

                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() =>
                            saveZone(zone.id)
                          }
                          className="rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-900"
                        >
                          Save
                        </button>

                        <button
                          type="button"
                          onClick={cancelEditing}
                          className="rounded-lg bg-slate-800 px-3 py-2 text-sm text-slate-300"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                        <div>
                          <h4 className="font-semibold">
                            {zone.name}
                          </h4>

                          <p className="mt-1 text-sm text-slate-400">
                            Moisture:{" "}
                            {zone.moisture_threshold_low} –{" "}
                            {zone.moisture_threshold_high}
                          </p>
                        </div>

                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={() =>
                              startEditing(zone)
                            }
                            className="rounded-lg bg-slate-800 px-3 py-2 text-sm text-slate-300 hover:bg-slate-700"
                          >
                            Edit
                          </button>

                          <button
                            type="button"
                            onClick={() =>
                              deleteZone(zone.id)
                            }
                            className="rounded-lg border border-red-800 px-3 py-2 text-sm text-red-300 hover:bg-red-950"
                          >
                            Delete
                          </button>
                        </div>
                      </div>

                      <p className="mt-3 font-mono text-xs text-slate-600">
                        Zone ID: {zone.id}
                      </p>
                    </>
                  )}
                </div>
              ))}

              {zones.length === 0 && (
                <p className="text-sm text-slate-500">
                  No zones configured.
                </p>
              )}
            </div>
          </section>

          <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <div>
              <h3 className="text-xl font-semibold">
                Device Assignments
              </h3>

              <p className="mt-1 text-sm text-slate-400">
                Assign devices to zones. The location is derived
                automatically from the selected zone.
              </p>
            </div>

            <div className="mt-6 space-y-4">
              {devices.length === 0 && (
                <p className="text-sm text-slate-500">
                  No devices available.
                </p>
              )}

              {devices.map((device) => {
                const currentZone = zones.find(
                  (zone) => zone.id === device.zone_id,
                );

                return (
                  <div
                    key={device.id}
                    className="rounded-xl border border-slate-800 bg-slate-950 p-5"
                  >
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                      <div>
                        <h4 className="font-semibold">
                          {device.display_name}
                        </h4>

                        <p className="mt-1 text-sm text-slate-400">
                          {device.device_type} ·{" "}
                          {device.role}
                        </p>
                      </div>

                      <select
                        value={currentZone?.id ?? ""}
                        onChange={(event) =>
                          assignDevice(
                            device.id,
                            event.target.value,
                          )
                        }
                        className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-white"
                      >
                        <option value="">
                          Unassigned
                        </option>

                        {zoneOptions.map((zone) => (
                          <option
                            key={zone.id}
                            value={zone.id}
                          >
                            {selectedLocation?.name} —{" "}
                            {zone.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="mt-3 text-xs text-slate-500">
                      Current assignment:{" "}
                      {currentZone
                        ? `${selectedLocation?.name} — ${currentZone.name}`
                        : "Unassigned"}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        </>
      )}
    </div>
  );
}