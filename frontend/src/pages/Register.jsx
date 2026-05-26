//Registration page for new customer/staff accounts. Form changes depending on if a staff or customer account is created.
import { useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest } from "../api/apiClient.js";

function Register() {
  const [formData, setFormData] = useState({
    role: "customer",
    full_name: "",
    email: "",
    password: "",
    phone: "",
    address: "",
    position: "",
  });

  const [message, setMessage] = useState("");
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

    setMessage("");
    setError("");

    const requestData = {
      role: formData.role,
      full_name: formData.full_name,
      email: formData.email,
      password: formData.password,
    };

    if (formData.role === "customer") {
      requestData.phone = formData.phone;
      requestData.address = formData.address;
    }

    if (formData.role === "staff") {
      requestData.position = formData.position;
    }

    try {
      const data = await apiRequest("/auth/register", {
        method: "POST",
        body: JSON.stringify(requestData),
      });

      setMessage(
        `Registration successful. Your account was created as a ${data.user.role}.`
      );

      setFormData({
        role: "customer",
        full_name: "",
        email: "",
        password: "",
        phone: "",
        address: "",
        position: "",
      });
    } catch (error) {
      setError(error.message);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Create Account</h1>

        <p className="auth-subtitle">
          Register as a customer or staff member to access IOTA Marketplace.
        </p>

        <form onSubmit={handleSubmit}>
          <p>
            <label>
              Account Type:
              <br />
              <select name="role" value={formData.role} onChange={handleChange}>
                <option value="customer">Customer</option>
                <option value="staff">Staff</option>
              </select>
            </label>
          </p>

          <p>
            <label>
              Full Name:
              <br />
              <input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                pattern="[A-Za-z\s'-]+"
                title="Full name cannot contain numbers."
                required
              />
            </label>
          </p>

          <p>
            <label>
              Email:
              <br />
              <input
                type="email"
                name="email"
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
                value={formData.password}
                onChange={handleChange}
                minLength="8"
                required
              />
            </label>
          </p>

          {formData.role === "customer" && (
            <>
              <p>
                <label>
                  Phone Number:
                  <br />
                  <input
                    type="text"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    pattern="04[0-9]{8}"
                    title="Phone number must start with 04 and contain 10 digits."
                    required
                  />
                </label>
              </p>

              <p>
                <label>
                  Address:
                  <br />
                  <input
                    type="text"
                    name="address"
                    value={formData.address}
                    onChange={handleChange}
                    required
                  />
                </label>
              </p>
            </>
          )}

          {formData.role === "staff" && (
            <p>
              <label>
                Position:
                <br />
                <input
                  type="text"
                  name="position"
                  value={formData.position}
                  onChange={handleChange}
                  pattern="[A-Za-z\s'-]+"
                  title="Position cannot contain numbers."
                  required
                />
              </label>
            </p>
          )}

          <button type="submit">Register</button>
        </form>

        {message && <p className="success-message">{message}</p>}
        {error && <p className="error-message">{error}</p>}

        <p>
          Already have an account? <Link to="/">Login here</Link>
        </p>
      </div>
    </div>
  );
}

export default Register;