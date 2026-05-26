// Displays the logged in user's dashboard. Edit this by adding a link from your feature to each page
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

function Dashboard() {
  const { user, isLoggedIn, loading } = useAuth();

  if (loading) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>Dashboard</h1>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>Dashboard</h1>
          <p>You must be logged in to view the dashboard.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header page-header-centered">
        <h1>Welcome {user?.full_name}</h1>
        <p>Select a feature below to continue.</p>
      </div>

      <section className="dashboard-grid">
        <Link className="feature-card" to="/access-logs">
          <h3>Feature 01</h3>
          <h2>User Access Management</h2>
          <p>View and search your login and logout history.</p>
        </Link>

        <div className="feature-card">
          <h3>Feature 02</h3>
          <h2>IoT Device Catalogue Management</h2>
          <p>Browse, search, and manage IoT device records.</p>
        </div>

        <div className="feature-card">
          <h3>Feature 03</h3>
          <h2>Orders</h2>
          <p>Create, view, update, and cancel customer orders.</p>
        </div>

        <div className="feature-card">
          <h3>Feature 04</h3>
          <h2>Payment Methods</h2>
          <p>Add, view, update, or delete saved payment methods.</p>
        </div>

        <div className="feature-card">
          <h3>Feature 05</h3>
          <h2>Payments</h2>
          <p>Make payments and view payment history.</p>
        </div>

        <div className="feature-card">
          <h3>Feature 06</h3>
          <h2>Shipments</h2>
          <p>View and manage shipment information.</p>
        </div>

        <div className="feature-card">
          <h3>Feature 07</h3>
          <h2>Shopping Cart</h2>
          <p>Add, remove, and order selected IoT devices.</p>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;