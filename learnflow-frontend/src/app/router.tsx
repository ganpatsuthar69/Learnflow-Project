import { createBrowserRouter } from "react-router-dom";
import Login from "../features/auth/pages/Login";
import SignUp from "../features/auth/pages/SignUp";
import VerifyOTP from "../features/auth/pages/VerifyOTP";
import PasswordReset from "../features/auth/pages/PasswordReset";
import ProtectedRoute from "../components/ProtectedRoute";
import Dashboard from "../features/Dashboard/Dashboard";
import StudyPlanPage from "../features/studyPlan/pages/StudyPlanPage";
import Profile from "../features/Profile/Profile.tsx"
import CreateProfile from "../features/Profile/CreateProfile";
import NotesPage from "../features/notes/pages/NotesPage";
import RoadmapPage from "../features/roadmap/pages/RoadmapPage";
import AiNotesPage from "../features/aiNotes/pages/AiNotesPage";
import QuizPage from "../features/quiz/pages/QuizPage";
import LandingPage from "../features/landing/LandingPage";


export const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPage />,
  },
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
        <CreateProfile />
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
  {
    path: "/study-plan",
    element: (
      <ProtectedRoute>
        <StudyPlanPage />
      </ProtectedRoute>
    ),
  },
  {
    path: "/notes",
    element: (
      <ProtectedRoute>
        <NotesPage />
      </ProtectedRoute>
    ),
  },
  {
    path: "/roadmap",
    element: (
      <ProtectedRoute>
        <RoadmapPage />
      </ProtectedRoute>
    ),
  },
  {
    path: "/ai-notes",
    element: (
      <ProtectedRoute>
        <AiNotesPage />
      </ProtectedRoute>
    ),
  },
  {
    path: "/quiz",
    element: (
      <ProtectedRoute>
        <QuizPage />
      </ProtectedRoute>
    ),
  },
]);