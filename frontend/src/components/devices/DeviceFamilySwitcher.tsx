import React from "react";

interface DeviceFamilySwitcherProps {
  currentFamily: "simulation" | "edge";
  onFamilyChange: (family: "simulation" | "edge") => void;
  onProvision: (family: "simulation" | "edge") => void;
  isProvisioning: boolean;
}

export const DeviceFamilySwitcher: React.FC<DeviceFamilySwitcherProps> = ({
  currentFamily,
  onFamilyChange,
  onProvision,
  isProvisioning,
}) => {
  return (
    <div className="flex flex-wrap items-center justify-between gap-4 p-4 mb-6 bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-gray-700">Hardware Family:</span>
        <div className="inline-flex rounded-md shadow-sm" role="group">
          <button
            type="button"
            onClick={() => onFamilyChange("simulation")}
            className={`px-4 py-2 text-sm font-medium rounded-l-lg border transition-colors ${
              currentFamily === "simulation"
                ? "bg-green-600 text-white border-green-600 shadow-inner"
                : "bg-white text-gray-900 border-gray-300 hover:bg-gray-100"
            }`}
          >
            Simulation Kit
          </button>
          <button
            type="button"
            onClick={() => onFamilyChange("edge")}
            className={`px-4 py-2 text-sm font-medium rounded-r-lg border-t border-b border-r transition-colors ${
              currentFamily === "edge"
                ? "bg-blue-600 text-white border-blue-600 shadow-inner"
                : "bg-white text-gray-900 border-gray-300 hover:bg-gray-100"
            }`}
          >
            Edge Hardware Kit
          </button>
        </div>
      </div>

      <div>
        <button
          type="button"
          onClick={() => onProvision(currentFamily)}
          disabled={isProvisioning}
          className={`px-4 py-2 text-sm font-medium text-white rounded-lg transition shadow-sm ${
            currentFamily === "simulation"
              ? "bg-green-600 hover:bg-green-700 disabled:bg-green-400"
              : "bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400"
          }`}
        >
          {isProvisioning
            ? "Provisioning Kit..."
            : `+ Provision ${currentFamily === "simulation" ? "Sim" : "Edge"} Kit`}
        </button>
      </div>
    </div>
  );
};
