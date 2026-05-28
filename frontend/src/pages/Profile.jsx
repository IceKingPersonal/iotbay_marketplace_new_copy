//Displays information of the logged in user's profile details.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest } from "../api/apiClient.js";
import { useAuth } from "../hooks/useAuth.js";

function Profile() {
  const { isLoggedIn, loading: authLoading } = useAuth();

  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchProfile() {
      try {
        const data = await apiRequest("/users/me");
        setProfile(data.user);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    }

    if (!authLoading && isLoggedIn) {
      fetchProfile();
    }
  }, [authLoading, isLoggedIn]);

  function formatText(value) {
    if (!value) {
      return "";
    }

    return value.charAt(0).toUpperCase() + value.slice(1);
  }

  if (authLoading) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>My Profile</h1>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>My Profile</h1>
          <p>You must be logged in to view your profile.</p>
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
          <h1>My Profile</h1>
          <p>Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>My Profile</h1>
          <p>{error || "Profile could not be loaded."}</p>
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
        <h1>View Profile</h1>
        <p>View your registered IOTA Marketplace account details.</p>
      </div>

      <section className="content-card">
        <div className="detail-section">
          <h3>Account Details</h3>

          <div className="detail-row">
            <span className="detail-label">User ID</span>
            <span>{profile.user_id}</span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Full Name</span>
            <span>{profile.full_name}</span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Email</span>
            <span>{profile.email}</span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Role</span>
            <span>{formatText(profile.role)}</span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Status</span>
            <span className="badge badge-blue">{formatText(profile.status)}</span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Member Since</span>
            <span>{profile.created_at}</span>
          </div>
        </div>

        {profile.role === "customer" && (
          <div className="detail-section">
            <h3>Customer Details</h3>

            <div className="detail-row">
              <span className="detail-label">Phone Number</span>
              <span>{profile.phone}</span>
            </div>

            <div className="detail-row">
              <span className="detail-label">Address</span>
              <span>{profile.address}</span>
            </div>
          </div>
        )}

        {profile.role === "staff" && (
          <div className="detail-section">
            <h3>Staff Details</h3>

            <div className="detail-row">
              <span className="detail-label">Staff ID</span>
              <span>{profile.staff_id}</span>
            </div>

            <div className="detail-row">
              <span className="detail-label">Position</span>
              <span>{profile.position}</span>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

export default Profile;
