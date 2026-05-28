//Defines the main frontend routes for the React app. Ensures pages accessible to non users doesn't display the navbar. For "logged in" pages e.g. features, make sure you add to this so the App layout uses the same navbar.
import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Profile from "./pages/Profile.jsx";
import EditProfile from "./pages/EditProfile.jsx";
import AccessLogs from "./pages/AccessLogs.jsx";
import Devices from "./pages/Devices.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import MakePayment from "./pages/MakePayment.jsx";
import PaymentHistory from "./pages/PaymentHistory.jsx";
import Orders from "./pages/Orders.jsx";
import OrderDetail from "./pages/OrderDetail.jsx";
import CreateOrder from "./pages/CreateOrder.jsx";
import Navbar from "./components/Navbar.jsx";
import ShipmentList from "./pages/ShipmentList.jsx";
import ShipmentDetail from "./pages/ShipmentDetail.jsx";
import CreateShipment from "./pages/CreateShipment.jsx";
import EditShipment from "./pages/EditShipment.jsx";

function AppLayout({ children }) {
  return (
    <>
      <Navbar />
      {children}
    </>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/dashboard"
        element={
          <AppLayout>
            <Dashboard />
          </AppLayout>
        }
      />

      <Route
        path="/profile"
        element={
          <AppLayout>
            <Profile />
          </AppLayout>
        }
      />

      <Route
        path="/edit"
        element={
          <AppLayout>
            <EditProfile />
          </AppLayout>
        }
      />

      <Route
        path="/access-logs"
        element={
          <AppLayout>
            <AccessLogs />
          </AppLayout>
        }
      />

      <Route
        path="/payments/create"
        element={
          <AppLayout>
            <MakePayment />
          </AppLayout>
        }
      />

      <Route
        path="/payments/history"
        element={
          <AppLayout>
            <PaymentHistory />
          </AppLayout>
        }
      />

      <Route
        path="/devices"
        element={
          <AppLayout>
            <Devices />
          </AppLayout>
        }
      />

      <Route
        path="/orders"
        element={
          <AppLayout>
            <Orders />
          </AppLayout>
        }
      />

      <Route
        path="/orders/new"
        element={
          <AppLayout>
            <CreateOrder />
          </AppLayout>
        }
      />

      <Route
        path="/orders/:orderId"
        element={
          <AppLayout>
            <OrderDetail />
          </AppLayout>
        }
      />

      <Route
        path="/shipments"
        element={
          <AppLayout>
            <ShipmentList />
          </AppLayout>
        }
      />

      <Route
        path="/shipments/create"
        element={
          <AppLayout>
            <CreateShipment />
          </AppLayout>
        }
      />

      <Route
        path="/shipments/:shipmentId"
        element={
          <AppLayout>
            <ShipmentDetail />
          </AppLayout>
        }
      />

      <Route
        path="/shipments/:shipmentId/edit"
        element={
          <AppLayout>
            <EditShipment />
          </AppLayout>
        }
      />
    </Routes>
  );
}

export default App;
