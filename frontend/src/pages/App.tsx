import { Code2 } from 'lucide-react';
import { NavLink, Outlet } from 'react-router-dom';

import { useAuth } from '../state/useAuth';

export default function App() {
  const { accessToken, logout } = useAuth();

  return (
    <main className="min-h-screen bg-paper">
      <header className="border-b border-ink/10 bg-white/75">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="grid size-10 place-items-center rounded bg-ink text-white">
              <Code2 aria-hidden="true" size={22} />
            </div>
            <div>
              <p className="text-lg font-semibold leading-6">AI Code Mentor</p>
              <p className="text-sm text-ink/60">Learning workspace</p>
            </div>
          </div>
          <nav className="flex items-center gap-2">
            {accessToken ? (
              <>
                <NavLink className="px-3 py-2 text-sm font-medium text-ink/75" to="/workspace">
                  Workspace
                </NavLink>
                <NavLink className="px-3 py-2 text-sm font-medium text-ink/75" to="/problems">
                  Problems
                </NavLink>
                <NavLink className="px-3 py-2 text-sm font-medium text-ink/75" to="/sheets">
                  Pattern Sheets
                </NavLink>
                <NavLink className="px-3 py-2 text-sm font-medium text-ink/75" to="/progress">
                  Progress
                </NavLink>
                <NavLink className="px-3 py-2 text-sm font-medium text-ink/75" to="/profile">
                  Profile
                </NavLink>
                <button
                  type="button"
                  onClick={logout}
                  className="rounded border border-ink/15 px-4 py-2 text-sm font-medium text-ink hover:bg-ink hover:text-white"
                >
                  Sign out
                </button>
              </>
            ) : (
              <>
                <NavLink className="px-3 py-2 text-sm font-medium text-ink/75" to="/login">
                  Log in
                </NavLink>
                <NavLink
                  className="rounded bg-coral px-4 py-2 text-sm font-semibold text-white hover:bg-coral/90"
                  to="/signup"
                >
                  Sign up
                </NavLink>
              </>
            )}
          </nav>
        </div>
      </header>
      <Outlet />
    </main>
  );
}
