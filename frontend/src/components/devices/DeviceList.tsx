import React, { useEffect, useState } from "react";
import {
  fetchDevices,
  provisionDeviceKit,
  type DeviceDto,
} from "../../services/api";
import { DeviceFamilySwitcher } from "./DeviceFamilySwitcher";

export const DeviceList: React.FC = () => {
  const [devices, setDevices] = useState<DeviceDto[]>([]);
  const [selectedFamily, setSelectedFamily] = useState<"simulation" | "edge">("simulation");
  const [roleFilter, setRoleFilter] = useState<"all" | "sensor" | "actuator">("all");
  const [loading, setLoading] = useState<boolean>(true);
  const [isProvisioning, setIsProvisioning] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadDevices = async () => {
    try {
      setLoading(true);
      setError(null);
      const roleParam = roleFilter === "all" ? undefined : roleFilter;
      const data = await fetchDevices(selectedFamily, roleParam);
      setDevices(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(`Failed to load devices: ${err.message}`);
      } else {
        setError("An unknown error occurred while loading devices.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDevices();
  }, [selectedFamily, roleFilter]);

  const handleProvisionKit = async (family: "simulation" | "edge") => {
    try {
      setIsProvisioning(true);
      setError(null);
      await provisionDeviceKit(family);
      await loadDevices();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(`Failed to provision kit: ${err.message}`);
      } else {
        setError("An unknown error occurred while provisioning.");
      }
    } finally {
      setIsProvisioning(false);
    }
  };

  const renderDate = (dateVal?: string) => {
    if (!dateVal) return "Recently";
    const d = new Date(dateVal);
    if (isNaN(d.getTime())) return "Recently";
    return d.toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="max-w-6xl mx-auto py-6 px-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-gray-200 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Greenhouse Device Families</h1>
          <p className="text-sm text-gray-500 mt-1">
            Provision and inspect devices via Abstract Factory architecture.
          </p>
        </div>

        <div className="mt-4 md:mt-0 flex items-center gap-2">
          <label htmlFor="role-filter" className="text-sm font-medium text-gray-700">
            Filter Role:
          </label>
          <select
            id="role-filter"
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value as "all" | "sensor" | "actuator")}
            className="rounded-md border border-gray-300 py-1.5 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="all">All Roles</option>
            <option value="sensor">Sensors Only</option>
            <option value="actuator">Actuators Only</option>
          </select>
        </div>
      </div>

      <DeviceFamilySwitcher
        currentFamily={selectedFamily}
        onFamilyChange={(fam) => setSelectedFamily(fam)}
        onProvision={handleProvisionKit}
        isProvisioning={isProvisioning}
      />

      {error && (
        <div className="p-4 mb-6 rounded-md bg-red-50 border border-red-200 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-12 text-gray-500 text-sm">
          Loading devices for {selectedFamily} family...
        </div>
      ) : devices.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-dashed border-gray-300 p-6">
          <p className="text-gray-500 text-sm">
            No devices found for the <strong>{selectedFamily}</strong> family.
          </p>
          <button
            type="button"
            onClick={() => handleProvisionKit(selectedFamily)}
            className="mt-4 inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700"
          >
            Provision Default {selectedFamily === "simulation" ? "Sim" : "Edge"} Kit
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {devices.map((device) => (
            <div
              key={device.id}
              className="p-5 bg-white rounded-lg border border-gray-200 shadow-sm flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span
                    className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                      device.role === "sensor"
                        ? "bg-sky-100 text-sky-800"
                        : "bg-amber-100 text-amber-800"
                    }`}
                  >
                    {device.role.toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-400">ID: #{device.id}</span>
                </div>

                <h3 className="text-base font-semibold text-gray-800">{device.display_name}</h3>
                <p className="text-xs text-gray-500 mb-3">Type: {device.device_type}</p>

                <div className="mt-2 bg-gray-50 p-2.5 rounded border border-gray-100">
                  <p className="text-xs font-medium text-gray-600 mb-1">Default Configuration:</p>
                  <pre className="text-xs text-gray-700 overflow-x-auto">
                    {JSON.stringify(device.default_config, null, 2)}
                  </pre>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-400">
                <span>Family: {device.device_family}</span>
                <span>Created: {renderDate(device.created_at)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
