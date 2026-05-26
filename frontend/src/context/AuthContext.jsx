//Stores and shares authentication state across React app. E.g. allows pages to check if a user is logged in or not.
import { createContext, useContext, useEffect, useState } from "react";
import { apiRequest } from "../api/apiClient";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  async function checkCurrentUser() {
    try {
      const data = await apiRequest("/auth/me");
      setUser(data.user);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    checkCurrentUser();
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

export function useAuth() {
  return useContext(AuthContext);
}