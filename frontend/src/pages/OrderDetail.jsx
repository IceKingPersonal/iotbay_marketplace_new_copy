// Feature 03 — Order detail
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { getOrder, patchOrderStatus } from "../api/orders.js";
import { useAuth } from "../hooks/useAuth.js";

function formatMoney(cents) {
  return (cents / 100).toFixed(2);
}

function statusClass(status) {
  if (status === "Paid") return "order-status order-status--paid";
  if (status === "Cancelled") return "order-status order-status--cancelled";
  return "order-status order-status--saved";
}

function OrderDetail() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const { user, isLoggedIn, loading: authLoading } = useAuth();
  const isStaff = user?.role === "staff";
  const id = Number(orderId);

  const [order, setOrder] = useState(null);
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function loadOrder() {
    setError("");
    try {
      const data = await getOrder(id);
      setOrder(data.order);
      setItems(data.items);
    } catch (err) {
      setError(err.message);
      navigate("/orders", { replace: true });
    }
  }

  useEffect(() => {
    if (authLoading || !isLoggedIn || !Number.isInteger(id) || id < 1) {
      return;
    }

    let isActive = true;

    async function fetchInitialOrder() {
      try {
        const data = await getOrder(id);

        if (isActive) {
          setOrder(data.order);
          setItems(data.items);
        }
      } catch (err) {
        if (isActive) {
          setError(err.message);
          navigate("/orders", { replace: true });
        }
      }
    }

    fetchInitialOrder();

    return () => {
      isActive = false;
    };
  }, [authLoading, id, isLoggedIn, navigate]);

  async function updateStatus(status) {
    setBusy(true);
    setError("");
    try {
      await patchOrderStatus(id, status);
      await loadOrder();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (authLoading) {
    return (
      <div className="page">
        <h1>Order</h1>
        <p>Loading...</p>
      </div>
    );
  }

  if (!isLoggedIn) {
    return (
      <div className="page">
        <h1>Order</h1>
        <p>You must be logged in.</p>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="page">
        <h1>Order</h1>
        <p>Loading order...</p>
      </div>
    );
  }

  const canManage = !isStaff && order.status === "Saved";

  return (
    <div className="page">
      <h1>Order #{order.order_id}</h1>
      <p className="muted">
        <Link to="/orders">Back to orders</Link>
      </p>

      {error ? <p className="form-error">{error}</p> : null}

      <div className="card form">
        <p>
          <strong>Status:</strong>{" "}
          <span className={statusClass(order.status)}>{order.status}</span>
        </p>
        <p>
          <strong>Total:</strong> {formatMoney(order.total_price)} {order.currency}
        </p>
        <p>
          <strong>Placed:</strong> {order.created_at}
        </p>
        <p>
          <strong>Ship to:</strong> {order.shipping_address}
        </p>
      </div>

      <h2>Devices</h2>
      <ul className="product-list">
        {items.map((line) => (
          <li key={line.order_item_id} className="card product-card">
            <div>
              <strong>{line.device_name || `Product #${line.product_id}`}</strong>
              {line.manufacturer || line.type ? (
                <div className="muted">
                  {[line.manufacturer, line.type].filter(Boolean).join(" · ")}
                </div>
              ) : null}
              <div className="muted">Qty: {line.quantity}</div>
            </div>
            <div className="product-meta">
              <span>{formatMoney(line.unit_price)} each</span>
              <span>
                {formatMoney(line.quantity * line.unit_price)} {order.currency}
              </span>
            </div>
          </li>
        ))}
      </ul>

      {order.status === "Cancelled" ? (
        <p className="muted">This order was cancelled. Stock has been restored.</p>
      ) : null}

      {canManage ? (
        <div className="card form">
          <h2>Update order</h2>
          <p className="muted">Mark as paid or cancel while the order is still Saved.</p>
          <div className="form-actions">
            <button
              type="button"
              className="btn btn-primary"
              disabled={busy}
              onClick={() => updateStatus("Paid")}
            >
              Mark as paid
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              disabled={busy}
              onClick={() => updateStatus("Cancelled")}
            >
              Cancel order
            </button>
          </div>
        </div>
      ) : null}

      {isStaff ? (
        <p className="muted">Staff can view orders but cannot change order status.</p>
      ) : null}
    </div>
  );
}

export default OrderDetail;
