import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest, isUnauthorizedError } from "../api/apiClient.js";
import { useAuth } from "../hooks/useAuth.js";

const categories = [
  { value: "", label: "All types" },
  { value: "sensor", label: "Sensor" },
  { value: "actuator", label: "Actuator" },
  { value: "controller", label: "Controller" },
  { value: "gateway", label: "Gateway" },
  { value: "camera", label: "Camera" },
  { value: "wearable", label: "Wearable" },
  { value: "smart_home", label: "Smart Home" },
  { value: "industrial", label: "Industrial" },
  { value: "accessory", label: "Accessory" },
  { value: "other", label: "Other" },
];

const deviceTypes = categories.filter((category) => category.value !== "");

const conditions = [
  { value: "new", label: "New" },
  { value: "used", label: "Used" },
  { value: "refurbished", label: "Refurbished" },
];

const statuses = [
  { value: "active", label: "Active" },
  { value: "inactive", label: "Inactive" },
  { value: "archived", label: "Archived" },
];

const emptyDeviceForm = {
  name: "",
  category: "sensor",
  brand: "",
  model: "",
  description: "",
  price: "",
  stock_quantity: "",
  condition: "new",
  status: "active",
};

function getDevicesEndpoint(filters = {}) {
  const params = new URLSearchParams();

  if (filters.searchTerm) {
    params.append("q", filters.searchTerm);
  }

  if (filters.category) {
    params.append("category", filters.category);
  }

  if (filters.inStockOnly) {
    params.append("in_stock", "true");
  }

  const query = params.toString();

  return query ? `/devices?${query}` : "/devices";
}

function Devices() {
  const navigate = useNavigate();
  const {
    user,
    isLoggedIn,
    loading: authLoading,
    logout,
  } = useAuth();

  const [devices, setDevices] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [category, setCategory] = useState("");
  const [inStockOnly, setInStockOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [formError, setFormError] = useState("");
  const [deviceForm, setDeviceForm] = useState(emptyDeviceForm);
  const [editingDeviceId, setEditingDeviceId] = useState(null);
  const [selectedDeviceIds, setSelectedDeviceIds] = useState([]);

  const isStaff = user?.role === "staff";

  function getCurrentFilters() {
    return {
      searchTerm,
      category,
      inStockOnly,
    };
  }

  function resetDeviceForm() {
    setDeviceForm(emptyDeviceForm);
    setEditingDeviceId(null);
    setFormError("");
  }

  const handleUnauthorizedApiError = useCallback(async (error) => {
    if (!isUnauthorizedError(error)) {
      return false;
    }

    setDevices([]);
    setSearchTerm("");
    setCategory("");
    setInStockOnly(false);
    setSelectedDeviceIds([]);
    setDeviceForm(emptyDeviceForm);
    setEditingDeviceId(null);
    setError("");
    setSuccess("");
    setFormError("");
    setLoading(false);
    setSubmitting(false);

    await logout();
    navigate("/");

    return true;
  }, [logout, navigate]);

  async function fetchDevices(filters = {}) {
    setLoading(true);
    setError("");

    try {
      const endpoint = getDevicesEndpoint(filters);
      const data = await apiRequest(endpoint);

      setDevices(data.devices);
      setSelectedDeviceIds([]);
    } catch (error) {
      if (await handleUnauthorizedApiError(error)) {
        return;
      }

      setError(error.message);
      setDevices([]);
      setSelectedDeviceIds([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (authLoading || !isLoggedIn) {
      return;
    }

    let isActive = true;

    async function fetchInitialDevices() {
      try {
        const data = await apiRequest(getDevicesEndpoint());

        if (isActive) {
          setDevices(data.devices);
          setSelectedDeviceIds([]);
        }
      } catch (error) {
        if (await handleUnauthorizedApiError(error)) {
          return;
        }

        if (isActive) {
          setError(error.message);
          setDevices([]);
          setSelectedDeviceIds([]);
        }
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    }

    fetchInitialDevices();

    return () => {
      isActive = false;
    };
  }, [authLoading, handleUnauthorizedApiError, isLoggedIn]);

  function handleSearch(event) {
    event.preventDefault();
    setSuccess("");

    fetchDevices(getCurrentFilters());
  }

  function handleClearSearch() {
    setSearchTerm("");
    setCategory("");
    setInStockOnly(false);
    setSuccess("");
    fetchDevices();
  }

  function handleDeviceFormChange(event) {
    const { name, value } = event.target;

    setDeviceForm({
      ...deviceForm,
      [name]: value,
    });
  }

  function handleEditDevice(device) {
    setEditingDeviceId(device.device_id);
    setFormError("");
    setSuccess("");
    setDeviceForm({
      name: device.name || "",
      category: device.category || "sensor",
      brand: device.brand || "",
      model: device.model || "",
      description: device.description || "",
      price: device.price ?? "",
      stock_quantity: device.stock_quantity ?? "",
      condition: device.condition || "new",
      status: device.status || "active",
    });
  }

  async function handleDeviceFormSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setSuccess("");
    setFormError("");

    const endpoint = editingDeviceId
      ? `/devices/${editingDeviceId}`
      : "/devices";
    const method = editingDeviceId ? "PUT" : "POST";

    try {
      await apiRequest(endpoint, {
        method,
        body: JSON.stringify(deviceForm),
      });

      setSuccess(
        editingDeviceId
          ? "Device updated successfully."
          : "Device created successfully."
      );
      resetDeviceForm();
      await fetchDevices(getCurrentFilters());
    } catch (error) {
      if (await handleUnauthorizedApiError(error)) {
        return;
      }

      setFormError(error.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function archiveDevice(deviceId) {
    setSubmitting(true);
    setError("");
    setSuccess("");
    setFormError("");

    try {
      await apiRequest(`/devices/${deviceId}`, {
        method: "DELETE",
      });

      setSuccess("Device archived successfully.");
      setSelectedDeviceIds((currentIds) => (
        currentIds.filter((currentId) => currentId !== deviceId)
      ));
      await fetchDevices(getCurrentFilters());
    } catch (error) {
      if (await handleUnauthorizedApiError(error)) {
        return;
      }

      setError(error.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleArchiveDevice(device) {
    const confirmed = window.confirm(
      `Archive ${device.name}? It will be removed from the catalogue.`
    );

    if (!confirmed) {
      return;
    }

    await archiveDevice(device.device_id);
  }

  async function handleBulkArchive() {
    if (selectedDeviceIds.length === 0) {
      setError("Select at least one device to archive.");
      return;
    }

    const confirmed = window.confirm(
      `Archive ${selectedDeviceIds.length} selected device record(s)?`
    );

    if (!confirmed) {
      return;
    }

    setSubmitting(true);
    setError("");
    setSuccess("");
    setFormError("");

    try {
      await apiRequest("/devices", {
        method: "DELETE",
        body: JSON.stringify({
          device_ids: selectedDeviceIds,
        }),
      });

      setSuccess("Selected devices archived successfully.");
      setSelectedDeviceIds([]);
      await fetchDevices(getCurrentFilters());
    } catch (error) {
      if (await handleUnauthorizedApiError(error)) {
        return;
      }

      setError(error.message);
    } finally {
      setSubmitting(false);
    }
  }

  function handleSelectDevice(deviceId) {
    setSelectedDeviceIds((currentIds) => {
      if (currentIds.includes(deviceId)) {
        return currentIds.filter((currentId) => currentId !== deviceId);
      }

      return [...currentIds, deviceId];
    });
  }

  function handleSelectAllDevices(event) {
    if (event.target.checked) {
      setSelectedDeviceIds(devices.map((device) => device.device_id));
      return;
    }

    setSelectedDeviceIds([]);
  }

  function formatText(value) {
    if (!value) {
      return "";
    }

    return value
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  }

  function formatPrice(value) {
    return `$${Number(value).toFixed(2)}`;
  }

  const allDevicesSelected = (
    devices.length > 0 && selectedDeviceIds.length === devices.length
  );

  if (authLoading) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>IoT Device Catalogue</h1>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>IoT Device Catalogue</h1>
          <p>You must be logged in to view the device catalogue.</p>
        </div>

        <Link className="button" to="/">
          Go to Login
        </Link>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header page-header-centered">
        <h1>IoT Device Catalogue</h1>
        <p>Browse and search available IoT device records.</p>
      </div>

      {isStaff && (
        <section className="content-card device-management-card">
          <h2>{editingDeviceId ? "Edit Device" : "Add Device"}</h2>

          <form onSubmit={handleDeviceFormSubmit} className="device-form">
            <div className="device-form-grid">
              <label>
                Device Name:
                <input
                  type="text"
                  name="name"
                  value={deviceForm.name}
                  onChange={handleDeviceFormChange}
                  maxLength="120"
                  required
                />
              </label>

              <label>
                Type:
                <select
                  name="category"
                  value={deviceForm.category}
                  onChange={handleDeviceFormChange}
                  required
                >
                  {deviceTypes.map((item) => (
                    <option key={item.value} value={item.value}>
                      {item.label}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Brand:
                <input
                  type="text"
                  name="brand"
                  value={deviceForm.brand}
                  onChange={handleDeviceFormChange}
                  maxLength="80"
                  required
                />
              </label>

              <label>
                Model:
                <input
                  type="text"
                  name="model"
                  value={deviceForm.model}
                  onChange={handleDeviceFormChange}
                  maxLength="80"
                  required
                />
              </label>

              <label>
                Unit Price:
                <input
                  type="number"
                  name="price"
                  value={deviceForm.price}
                  onChange={handleDeviceFormChange}
                  min="0"
                  max="100000"
                  step="0.01"
                  required
                />
              </label>

              <label>
                Stock:
                <input
                  type="number"
                  name="stock_quantity"
                  value={deviceForm.stock_quantity}
                  onChange={handleDeviceFormChange}
                  min="0"
                  max="100000"
                  step="1"
                  required
                />
              </label>

              <label>
                Condition:
                <select
                  name="condition"
                  value={deviceForm.condition}
                  onChange={handleDeviceFormChange}
                  required
                >
                  {conditions.map((item) => (
                    <option key={item.value} value={item.value}>
                      {item.label}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Status:
                <select
                  name="status"
                  value={deviceForm.status}
                  onChange={handleDeviceFormChange}
                  required
                >
                  {statuses.map((item) => (
                    <option key={item.value} value={item.value}>
                      {item.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <label>
              Description:
              <textarea
                name="description"
                value={deviceForm.description}
                onChange={handleDeviceFormChange}
                maxLength="1000"
                rows="3"
              />
            </label>

            <div className="device-form-actions">
              <button type="submit" disabled={submitting}>
                {editingDeviceId ? "Save Changes" : "Create Device"}
              </button>

              {editingDeviceId && (
                <button
                  type="button"
                  className="button-secondary"
                  onClick={resetDeviceForm}
                  disabled={submitting}
                >
                  Cancel Edit
                </button>
              )}
            </div>
          </form>

          {formError && <p className="error-message">{formError}</p>}
        </section>
      )}

      <section className="content-card devices-card">
        <form onSubmit={handleSearch} className="device-search">
          <label>
            Search Devices:
            <input
              type="search"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Name, type, brand, model, or description"
            />
          </label>

          <label>
            Type:
            <select
              value={category}
              onChange={(event) => setCategory(event.target.value)}
            >
              {categories.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>

          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={inStockOnly}
              onChange={(event) => setInStockOnly(event.target.checked)}
            />
            In stock only
          </label>

          <div className="device-actions">
            <button type="submit">Search</button>

            <button type="button" onClick={handleClearSearch}>
              Clear Search
            </button>
          </div>
        </form>

        {success && <p className="success-message">{success}</p>}

        {isStaff && devices.length > 0 && (
          <div className="device-bulk-actions">
            <span>{selectedDeviceIds.length} selected</span>
            <button
              type="button"
              className="danger-button"
              onClick={handleBulkArchive}
              disabled={submitting || selectedDeviceIds.length === 0}
            >
              Archive Selected
            </button>
          </div>
        )}

        {loading && <p>Loading devices...</p>}

        {error && <p className="error-message">{error}</p>}

        {!loading && !error && devices.length === 0 && (
          <p>No devices found.</p>
        )}

        {!loading && !error && devices.length > 0 && (
          <div className="table-wrapper">
            <table className="device-table">
              <thead>
                <tr>
                  {isStaff && (
                    <th className="select-column">
                      <input
                        type="checkbox"
                        checked={allDevicesSelected}
                        onChange={handleSelectAllDevices}
                        aria-label="Select all devices"
                      />
                    </th>
                  )}
                  <th>Device</th>
                  <th>Type</th>
                  <th>Brand</th>
                  <th>Model</th>
                  <th>Condition</th>
                  <th>Price</th>
                  <th>Stock</th>
                  {isStaff && <th>Actions</th>}
                </tr>
              </thead>

              <tbody>
                {devices.map((device) => (
                  <tr key={device.device_id}>
                    {isStaff && (
                      <td className="select-column">
                        <input
                          type="checkbox"
                          checked={selectedDeviceIds.includes(device.device_id)}
                          onChange={() => handleSelectDevice(device.device_id)}
                          aria-label={`Select ${device.name}`}
                        />
                      </td>
                    )}
                    <td>
                      <strong>{device.name}</strong>
                      {device.description && (
                        <span className="device-description">
                          {device.description}
                        </span>
                      )}
                    </td>
                    <td>{formatText(device.category)}</td>
                    <td>{device.brand}</td>
                    <td>{device.model}</td>
                    <td>{formatText(device.condition)}</td>
                    <td>{formatPrice(device.price)}</td>
                    <td>{device.stock_quantity}</td>
                    {isStaff && (
                      <td>
                        <div className="row-actions">
                          <button
                            type="button"
                            className="button-secondary"
                            onClick={() => handleEditDevice(device)}
                            disabled={submitting}
                          >
                            Edit
                          </button>
                          <button
                            type="button"
                            className="danger-button"
                            onClick={() => handleArchiveDevice(device)}
                            disabled={submitting}
                          >
                            Archive
                          </button>
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

export default Devices;
