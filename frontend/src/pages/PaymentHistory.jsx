// Feature 05 – Payment History
// Customers see their own payments; staff see all customer payments with customer ID and name.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest } from "../api/apiClient.js";
import { useAuth } from "../hooks/useAuth.js";

function PaymentHistory() {
  const { user } = useAuth();
  const [payments, setPayments] = useState([]);
  const [role, setRole] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchHistory() {
      try {
        const data = await apiRequest("/payments/history");
        setPayments(data.payments);
        setRole(data.role);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchHistory();
  }, []);

  if (loading) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>Payment History</h1>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header page-header-centered">
        <h1>{role === "staff" ? "All Customer Payments" : "Your Payment History"}</h1>
        <p>
          {role === "staff"
            ? `Viewing all payments as staff${user?.staff_id ? ` (${user.staff_id})` : ""}.`
            : `Viewing payments for user ID: ${user?.user_id}.`}
        </p>
      </div>

      <section className="content-card payments-card">
        {error && <p className="error-message">{error}</p>}

        {!error && payments.length === 0 && <p>No payments found.</p>}

        {!error && payments.length > 0 && (
          <div className="table-wrapper">
            <table className="payments-table">
              <thead>
                <tr>
                  <th>Payment ID</th>
                  <th>Order ID</th>
                  {role === "staff" && <th>Customer ID</th>}
                  {role === "staff" && <th>Customer Name</th>}
                  <th>Amount</th>
                  <th>Payment Method</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {payments.map((payment) => (
                  <tr key={payment.payment_id}>
                    <td>#{payment.payment_id}</td>
                    <td>#{payment.order_id}</td>
                    {role === "staff" && <td>{payment.customer_id}</td>}
                    {role === "staff" && <td>{payment.full_name}</td>}
                    <td>${Number(payment.amount).toFixed(2)}</td>
                    <td>{payment.payment_type}</td>
                    <td>{payment.payment_date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {role === "customer" && (
          <div className="payment-actions">
            <Link className="button" to="/payments/create">
              Make a Payment
            </Link>
          </div>
        )}
      </section>
    </div>
  );
}

export default PaymentHistory;
