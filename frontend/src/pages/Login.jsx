//Main login page for application. Sends user's email/password to Flask backend. If login is successful it saves it in AuthContext and it redirects users to the dashboard page.
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest } from "../api/apiClient.js";
import { useAuth } from "../context/AuthContext.jsx";

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData({
      ...formData,
      [name]: value,
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");

    try {
      const data = await apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify(formData),
      });

      login(data.user);
      navigate("/dashboard");
    } catch (error) {
      setError(error.message);
    }
  }

  return (
  <div className="login-page">
    <div className="login-card">
      <h1>IOTA Marketplace</h1>

      <form onSubmit={handleSubmit}>
        <p>
          <label>
            Email:
            <br />
            <input
              type="email"
              name="email"
              placeholder="Enter email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </label>
        </p>

        <p>
          <label>
            Password:
            <br />
            <input
              type="password"
              name="password"
              placeholder="Enter password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </label>
        </p>

        <button type="submit">Login</button>
      </form>

      {error && <p className="error-message">{error}</p>}

      <p>
        Not a user? <Link to="/register">Register here</Link>
      </p>
    </div>
  </div>
);
}

export default Login;