//Feature 1 - Adrian Voljak
//useState stores changing values on the page. useEffect runs code automatically when the component loads for the first time.
import { useEffect, useState } from "react";

//Imports the API helper used to send requests to backend.
import { apiRequest } from "../api/apiClient.js";
import { useAuth } from "../context/AuthContext.jsx";

//Displays the logged-in user's access logs. They can view their login/logout history and search logs by the date.
function AccessLogs() {
  const { isLoggedIn, loading: authLoading } = useAuth();

  const [logs, setLogs] = useState([]);
  const [searchDate, setSearchDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  //Fetches access logs from backend. If no date is provided it shows all logs for user. If a date is provided it shows that specific dates logs.
  async function fetchLogs(date = "") {
    setLoading(true);
    setError("");

    try {
      let endpoint = "/access-logs/me";

      if (date) {
        endpoint = `/access-logs/me?date=${date}`;
      }

      const data = await apiRequest(endpoint);
      setLogs(data.logs);
    } catch (error) {
      setError(error.message);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!authLoading && isLoggedIn) {
      fetchLogs();
    }
  }, [authLoading, isLoggedIn]);

  function handleSearch(event) {
    event.preventDefault();
    fetchLogs(searchDate);
  }

  function handleClearSearch() {
    setSearchDate("");
    fetchLogs();
  }

  if (authLoading) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>My Access Logs</h1>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>My Access Logs</h1>
          <p>You must be logged in to view your access logs.</p>
        </div>
      </div>
    );
  }

  //Page design and layout
  return (
    <div className="page">
      <div className="page-header page-header-centered">
        <h1>My Access Logs</h1>
        <p>View and search your login and logout history.</p>
      </div>

      <section className="content-card access-logs-card">
        <form onSubmit={handleSearch} className="access-log-search">
          <label>
            Search by Date:
            <input
              type="date"
              value={searchDate}
              onChange={(event) => setSearchDate(event.target.value)}
            />
          </label>

          <div className="access-log-actions">
            <button type="submit">Search</button>

            <button type="button" onClick={handleClearSearch}>
              Clear Search
            </button>
          </div>
        </form>

        {loading && <p>Loading access logs...</p>}

        {error && <p className="error-message">{error}</p>}

        {!loading && !error && logs.length === 0 && (
          <p>No access logs found.</p>
        )}

        {!loading && !error && logs.length > 0 && (
          <div className="table-wrapper">
            <table className="access-log-table">
              <thead>
                <tr>
                  <th>Log ID</th>
                  <th>User ID</th>
                  <th>Login Time</th>
                  <th>Logout Time</th>
                  <th>Created At</th>
                </tr>
              </thead>

              <tbody>
                {logs.map((log) => (
                  <tr key={log.log_id}>
                    <td>{log.log_id}</td>
                    <td>{log.user_id}</td>
                    <td>{log.login_time}</td>
                    <td>
                      {log.logout_time || "Still logged in / no logout recorded"}
                    </td>
                    <td>{log.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

export default AccessLogs;