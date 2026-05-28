// Feature 05 – Make a Payment (customers only)
import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { apiRequest } from "../api/apiClient.js";
import { useAuth } from "../hooks/useAuth.js";

function MakePayment() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  const [orders, setOrders] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState("");
  const [selectedMethod, setSelectedMethod] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    if (!authLoading && user?.role !== "customer") {
      navigate("/payments/history");
      return;
    }

    if (authLoading) return;

    async function fetchFormData() {
      try {
        const data = await apiRequest("/payments/create");
        setOrders(data.orders);
        setPaymentMethods(data.payment_methods);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchFormData();
  }, [authLoading, user, navigate]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setSubmitting(true);

    try {
      const data = await apiRequest("/payments/create", {
        method: "POST",
        body: JSON.stringify({
          order_id: parseInt(selectedOrder),
          payment_method_id: parseInt(selectedMethod),
        }),
      });
      setSuccess(data.message);
      setOrders((prev) => prev.filter((o) => o.order_id !== parseInt(selectedOrder)));
      setSelectedOrder("");
      setSelectedMethod("");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (authLoading || loading) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>Make a Payment</h1>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header page-header-centered">
        <h1>Make a Payment</h1>
        <p>Select a saved order and payment method to complete your payment.</p>
      </div>

      <section className="content-card">
        {error && <p className="error-message">{error}</p>}
        {success && <p className="success-message">{success}</p>}

        {orders.length === 0 && paymentMethods.length === 0 ? (
          <p>
            You have no saved orders and no payment methods on file. Please place an order and
            add a payment method before paying.
          </p>
        ) : orders.length === 0 ? (
          <p>You have no saved orders ready for payment.</p>
        ) : paymentMethods.length === 0 ? (
          <p>You have no payment methods on file. Please add a payment method before paying.</p>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="detail-section">
              <label>
                Order to pay
                <select
                  value={selectedOrder}
                  onChange={(e) => setSelectedOrder(e.target.value)}
                  required
                >
                  <option value="" disabled>
                    Choose a saved order…
                  </option>
                  {orders.map((order) => (
                    <option key={order.order_id} value={order.order_id}>
                      Order #{order.order_id} — ${Number(order.total_price).toFixed(2)} (
                      {order.order_date})
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="detail-section">
              <label>
                Payment method
                <select
                  value={selectedMethod}
                  onChange={(e) => setSelectedMethod(e.target.value)}
                  required
                >
                  <option value="" disabled>
                    Choose a payment method…
                  </option>
                  {paymentMethods.map((method) => (
                    <option key={method.payment_method_id} value={method.payment_method_id}>
                      {method.payment_type} — {method.details}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="payment-actions">
              <button type="submit" disabled={submitting}>
                {submitting ? "Processing..." : "Confirm Payment"}
              </button>
              <Link className="button button-secondary" to="/payments/history">
                View Payment History
              </Link>
            </div>
          </form>
        )}
      </section>
    </div>
  );
}

export default MakePayment;
