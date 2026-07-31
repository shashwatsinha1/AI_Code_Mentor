import React from 'react';
import { Navigate } from 'react-router-dom';

import { useAuth } from '../state/useAuth';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { accessToken, isAuthReady } = useAuth();
  if (!isAuthReady) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-12 text-sm font-medium text-ink/65 sm:px-6">
        Loading session...
      </div>
    );
  }
  return accessToken ? children : <Navigate to="/login" replace />;
}
