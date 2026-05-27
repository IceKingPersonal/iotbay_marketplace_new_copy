// Feature 03 — Orders
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listOrders } from "../api/orders.js";
import { useAuth } from "../context/AuthContext.jsx";

function formatMoney(cents) {
  return (cents / 100).toFixed(2);
}

function statusClass(status) {
  if (status === "Paid") return "order-status order-status--paid";
  if (status === "Cancelled") return "order-status order-status--cancelled";
  return "order-status order-status--saved";
}

function Orders() {
  const { user, isLoggedIn, loading: authLoading } = useAuth();
  const isStaff = user?.role === "staff";

  const [orders, setOrders] = useState([]);
  const [orderIdQuery, setOrderIdQuery] = useState("");
  const [dateQuery, setDateQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function fetchOrders(filters = {}) {
    setLoading(true);
    setError("");
    try {
      const data = await listOrders(filters);
      setOrders(data.orders);
    } catch (err) {
      setError(err.message);
      setOrders([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!authLoading && isLoggedIn) {
      fetchOrders();
    }
  }, [authLoading, isLoggedIn]);

  function handleSearch(event) {
    event.preventDefault();
    const filters = {};
    const rawId = orderIdQuery.trim();
    if (rawId) {
      const n = Number(rawId);
      if (!Number.isInteger(n) || n < 1) {
        setError("Order ID must be a positive integer.");
        return;
      }
      filters.orderId = n;
    }
    if (dateQuery.trim()) {
      filters.date = dateQuery.trim();
    }
    fetchOrders(filters);
  }

  function handleClearSearch() {
    setOrderIdQuery("");
    setDateQuery("");
    fetchOrders();
  }

  if (authLoading) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>Orders</h1>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>Orders</h1>
          <p>You must be logged in to view orders.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header page-header-centered">
        <h1>{isStaff ? "Customer orders" : "My orders"}</h1>
        <p>
          {isStaff
            ? "View all customer orders (read-only)."
            : "New orders start as Saved. Search by order ID or date."}
        </p>
      </div>

      {!isStaff ? (
        <form className="card form" onSubmit={handleSearch}>
          <h2>Search</h2>
          <label className="field">
            <span>Order ID</span>
            <input
              value={orderIdQuery}
              onChange={(e) => setOrderIdQuery(e.target.value)}
              placeholder="e.g. 5"
            />
          </label>
          <label className="field">
            <span>Date (YYYY-MM-DD)</span>
            <input
              value={dateQuery}
              onChange={(e) => setDateQuery(e.target.value)}
              placeholder="e.g. 2026-05-27"
            />
          </label>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">
              Search
            </button>
            <button type="button" className="btn btn-secondary" onClick={handleClearSearch}>
              Clear
            </button>
          </div>
        </form>
      ) : null}

      {error ? <p className="form-error">{error}</p> : null}
      {loading ? <p>Loading orders...</p> : null}

      {!loading && orders.length === 0 ? (
        <p className="muted">No orders found.</p>
      ) : null}

      <ul className="product-list">
        {orders.map((order) => (
          <li key={order.order_id} className="card product-card">
            <div>
              <strong>Order #{order.order_id}</strong>
              {isStaff && order.customer_name ? (
                <div className="muted">
                  {order.customer_name} ({order.customer_email})
                </div>
              ) : null}
              <div className="muted">{order.created_at}</div>
              <div className="muted">{order.shipping_address}</div>
            </div>
            <div className="product-meta">
              <span>
                {formatMoney(order.total_price)} {order.currency}
              </span>
              <span className={statusClass(order.status)}>{order.status}</span>
              <Link className="btn btn-secondary" to={`/orders/${order.order_id}`}>
                View
              </Link>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Orders;
