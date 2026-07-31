import React from 'react';
import ReactDOM from 'react-dom/client';
import { Navigate, RouterProvider, createBrowserRouter } from 'react-router-dom';

import ProtectedRoute from './components/ProtectedRoute';
import App from './pages/App';
import LoginPage from './pages/LoginPage';
import ProblemDetailPage from './pages/ProblemDetailPage';
import ProblemsPage from './pages/ProblemsPage';
import ProfilePage from './pages/ProfilePage';
import ProgressPage from './pages/ProgressPage';
import SheetDetailPage from './pages/SheetDetailPage';
import SheetsPage from './pages/SheetsPage';
import SignupPage from './pages/SignupPage';
import WorkspacePage from './pages/WorkspacePage';
import { AuthProvider } from './state/AuthContext';
import './styles.css';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <Navigate to="/profile" replace /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'signup', element: <SignupPage /> },
      {
        path: 'workspace',
        element: (
          <ProtectedRoute>
            <WorkspacePage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'problems',
        element: (
          <ProtectedRoute>
            <ProblemsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'problems/:slug',
        element: (
          <ProtectedRoute>
            <ProblemDetailPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'sheets',
        element: (
          <ProtectedRoute>
            <SheetsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'sheets/:slug',
        element: (
          <ProtectedRoute>
            <SheetDetailPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'progress',
        element: (
          <ProtectedRoute>
            <ProgressPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'profile',
        element: (
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        ),
      },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider>
      <RouterProvider router={router} future={{ v7_startTransition: true }} />
    </AuthProvider>
  </React.StrictMode>,
);
