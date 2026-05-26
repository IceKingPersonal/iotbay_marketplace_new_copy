//Allows the logged-in user to update their account details.
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest } from "../api/apiClient.js";
import { useAuth } from "../context/AuthContext.jsx";

function EditProfile() {
  const navigate = useNavigate();
  const { login, logout, isLoggedIn, loading: authLoading } = useAuth();

  const [formData, setFormData] = useState({
    role: "",
    full_name: "",
    email: "",
    phone: "",
    address: "",
    staff_id: "",
    position: "",
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    async function fetchProfile() {
      try {
        const data = await apiRequest("/users/me");

        setFormData({
          role: data.user.role || "",
          full_name: data.user.full_name || "",
          email: data.user.email || "",
          phone: data.user.phone || "",
          address: data.user.address || "",
          staff_id: data.user.staff_id || "",
          position: data.user.position || "",
        });
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    }

    if (!authLoading && isLoggedIn) {
      fetchProfile();
    }

    if (!authLoading && !isLoggedIn) {
      setLoading(false);
    }
  }, [authLoading, isLoggedIn]);

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
    setMessage("");

    const requestData = {
      full_name: formData.full_name,
      email: formData.email,
    };

    if (formData.role === "customer") {
      requestData.phone = formData.phone;
      requestData.address = formData.address;
    }

    if (formData.role === "staff") {
      requestData.position = formData.position;
    }

    try {
      const data = await apiRequest("/users/me", {
        method: "PUT",
        body: JSON.stringify(requestData),
      });

      login(data.user);
      setMessage("Profile updated successfully.");
      navigate("/profile");
    } catch (error) {
      setError(error.message);
    }
  }

  async function handleCancelAccount() {
    const confirmed = window.confirm(
      "Are you sure you want to cancel your account? This will make your account inactive."
    );

    if (!confirmed) {
      return;
    }

    try {
      await apiRequest("/users/me/cancel", {
        method: "PUT",
      });

      await logout();
      navigate("/");
    } catch (error) {
      setError(error.message);
    }
  }

  if (authLoading) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>Edit Profile</h1>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>Edit Profile</h1>
          <p>You must be logged in to edit your profile.</p>
        </div>

        <Link className="button" to="/">
          Go to Login
        </Link>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>Edit Profile</h1>
          <p>Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error && !formData.role) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>Edit Profile</h1>
          <p>{error}</p>
        </div>

        <Link className="button" to="/">
          Go to Login
        </Link>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header page-header-centered">
        <h1>Edit Profile</h1>
        <p>Update your account details or cancel your registration.</p>
      </div>

      <section className="content-card edit-profile-card">
        <h2>Edit Profile Details</h2>

        <form onSubmit={handleSubmit}>
          <p>
            <strong>Account Type:</strong>{" "}
            {formData.role.charAt(0).toUpperCase() + formData.role.slice(1)}
          </p>

          {formData.role === "staff" && (
            <p>
              <strong>Staff ID:</strong> {formData.staff_id}
            </p>
          )}

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

          <button type="submit">Save Changes</button>
        </form>

        {message && <p className="success-message">{message}</p>}
        {error && <p className="error-message">{error}</p>}
      </section>

      <section className="content-card cancel-account-card">
        <h2>Cancel Account</h2>

        <p>
          Cancelling your account will set your account status to inactive. Your
          account will remain in the database, but you will no longer be able to
          log in.
        </p>

        <button className="danger-button" onClick={handleCancelAccount}>
          Cancel Account
        </button>
      </section>
    </div>
  );
}

export default EditProfile;