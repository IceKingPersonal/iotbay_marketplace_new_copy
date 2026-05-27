//Defines the main frontend routes for the React app. Ensures pages accessible to non users doesn't display the navbar. For "logged in" pages e.g. features, make sure you add to this so the App layout uses the same navbar.
import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Profile from "./pages/Profile.jsx";
import EditProfile from "./pages/EditProfile.jsx";
import AccessLogs from "./pages/AccessLogs.jsx";
import Devices from "./pages/Devices.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Navbar from "./components/Navbar.jsx";

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
        path="/orders"
        element={
          <AppLayout>
            <Orders />
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
    </Routes>
  );
}

export default App;
