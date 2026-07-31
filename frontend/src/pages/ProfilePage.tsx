import { useEffect, useState } from 'react';
import { ShieldCheck } from 'lucide-react';

import { User, getMe } from '../api/client';
import { useAuth } from '../state/useAuth';

export default function ProfilePage() {
  const { accessToken, refresh, logout } = useAuth();
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadProfile() {
      if (!accessToken) {
        return;
      }
      try {
        const profile = await getMe(accessToken);
        if (isMounted) {
          setUser(profile);
        }
      } catch {
        try {
          const newAccessToken = await refresh();
          if (newAccessToken && isMounted) {
            setUser(await getMe(newAccessToken));
          }
        } catch (err) {
          if (isMounted) {
            setError(err instanceof Error ? err.message : 'Session expired');
            logout();
          }
        }
      }
    }

    loadProfile();
    return () => {
      isMounted = false;
    };
  }, [accessToken, refresh, logout]);

  return (
    <section className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <div className="rounded border border-ink/10 bg-white p-6 shadow-soft">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-sage">Protected route</p>
            <h1 className="mt-2 text-3xl font-bold text-ink">Profile</h1>
          </div>
          <div className="flex items-center gap-2 rounded bg-sage/10 px-3 py-2 text-sm font-semibold text-sage">
            <ShieldCheck aria-hidden="true" size={18} />
            JWT verified
          </div>
        </div>

        {error ? <p className="mt-6 text-sm font-medium text-red-700">{error}</p> : null}
        {!user && !error ? <p className="mt-8 text-ink/65">Loading profile...</p> : null}
        {user ? (
          <dl className="mt-8 grid gap-4 sm:grid-cols-2">
            <div className="border-t border-ink/10 pt-4">
              <dt className="text-sm text-ink/55">Name</dt>
              <dd className="mt-1 text-lg font-semibold">{user.full_name ?? 'Unnamed learner'}</dd>
            </div>
            <div className="border-t border-ink/10 pt-4">
              <dt className="text-sm text-ink/55">Email</dt>
              <dd className="mt-1 text-lg font-semibold">{user.email}</dd>
            </div>
            <div className="border-t border-ink/10 pt-4">
              <dt className="text-sm text-ink/55">Status</dt>
              <dd className="mt-1 text-lg font-semibold">{user.is_active ? 'Active' : 'Inactive'}</dd>
            </div>
            <div className="border-t border-ink/10 pt-4">
              <dt className="text-sm text-ink/55">Joined</dt>
              <dd className="mt-1 text-lg font-semibold">
                {new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(
                  new Date(user.created_at),
                )}
              </dd>
            </div>
          </dl>
        ) : null}
      </div>
    </section>
  );
}
