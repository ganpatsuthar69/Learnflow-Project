import { createBrowserRouter } from "react-router-dom";
import Login from "../features/auth/pages/Login";
import SignUp from "../features/auth/pages/SignUp";
import VerifyOTP from "../features/auth/pages/VerifyOTP";
import PasswordReset from "../features/auth/pages/PasswordReset";
import ProtectedRoute from "../components/ProtectedRoute";
import Dashboard from "../features/Dashboard/Dashboard";
import Profile from "../features/Profile/Profile.tsx"
import CreateProfile from "../features/Profile/CreateProfile";


export const router = createBrowserRouter([
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/signup",
    element: < SignUp />,
  },
  {
    path: "/verifyotp",
    element: <VerifyOTP />,
  },
  {
    path: "/reset-password",
    element: <PasswordReset />,
  },
  {
    path: "/dashboard",
    element: (
      <ProtectedRoute>
        <Dashboard />
      </ProtectedRoute>
    ),
  },
  {
    path: "/createprofile",
    element: (
      <ProtectedRoute>
        <CreateProfile/>
      </ProtectedRoute>
    ),
  },

  {
    path: "/profile",
    element: (
      <ProtectedRoute>
        <Profile />
      </ProtectedRoute>
    ),
  },
]);