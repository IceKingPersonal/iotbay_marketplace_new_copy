import { useEffect, useState } from "react";
import { apiRequest } from "../api/apiClient.js";

const categories = [
  { value: "", label: "All categories" },
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

function Devices() {
  const [devices, setDevices] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [category, setCategory] = useState("");
  const [inStockOnly, setInStockOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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

  async function fetchDevices(filters = {}) {
    setLoading(true);
    setError("");

    try {
      const endpoint = getDevicesEndpoint(filters);
      const data = await apiRequest(endpoint);

      setDevices(data.devices);
    } catch (error) {
      setError(error.message);
      setDevices([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let isActive = true;

    async function fetchInitialDevices() {
      try {
        const data = await apiRequest(getDevicesEndpoint());

        if (isActive) {
          setDevices(data.devices);
        }
      } catch (error) {
        if (isActive) {
          setError(error.message);
          setDevices([]);
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
  }, []);

  function handleSearch(event) {
    event.preventDefault();

    fetchDevices({
      searchTerm,
      category,
      inStockOnly,
    });
  }

  function handleClearSearch() {
    setSearchTerm("");
    setCategory("");
    setInStockOnly(false);
    fetchDevices();
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

  return (
    <div className="page">
      <div className="page-header page-header-centered">
        <h1>IoT Device Catalogue</h1>
        <p>Browse and search available IoT device records.</p>
      </div>

      <section className="content-card devices-card">
        <form onSubmit={handleSearch} className="device-search">
          <label>
            Search Devices:
            <input
              type="search"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Name, brand, model, or description"
            />
          </label>

          <label>
            Category:
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
                  <th>Device</th>
                  <th>Category</th>
                  <th>Brand</th>
                  <th>Model</th>
                  <th>Condition</th>
                  <th>Price</th>
                  <th>Stock</th>
                </tr>
              </thead>

              <tbody>
                {devices.map((device) => (
                  <tr key={device.device_id}>
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
