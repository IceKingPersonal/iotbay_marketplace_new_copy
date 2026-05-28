//Stores and shares authentication state across React app. E.g. allows pages to check if a user is logged in or not.
import { useEffect, useState } from "react";
import { apiRequest } from "../api/apiClient";
import { AuthContext } from "./AuthContextValue.js";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  async function checkCurrentUser() {
    try {
      const data = await apiRequest("/auth/me");
      setUser(data.user);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let isActive = true;

    async function loadCurrentUser() {
      try {
        const data = await apiRequest("/auth/me");

        if (isActive) {
          setUser(data.user);
        }
      } catch {
        if (isActive) {
          setUser(null);
        }
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    }

    loadCurrentUser();

    return () => {
      isActive = false;
    };
  }, []);

  function login(userData) {
    setUser(userData);
  }

  async function logout() {
    try {
      await apiRequest("/auth/logout", {
        method: "POST",
      });
    } catch (error) {
      console.error(error.message);
    } finally {
      setUser(null);
    }
  }

  const value = {
    user,
    isLoggedIn: user !== null,
    loading,
    login,
    logout,
    checkCurrentUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
