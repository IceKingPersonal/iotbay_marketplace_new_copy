import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

function Navbar() {
  const navigate = useNavigate();
  const { logout } = useAuth();

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/profile">View Profile</Link>
        <Link to="/edit">Edit Profile</Link>
      </div>

      <div className="navbar-center">IOTA Marketplace</div>

      <div className="navbar-right">
        <button className="navbar-logout" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </nav>
  );
}

export default Navbar;