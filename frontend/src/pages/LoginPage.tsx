import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { useAuth } from '../state/useAuth';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await login(email, password);
      navigate('/profile');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to log in');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="mx-auto grid max-w-6xl gap-8 px-4 py-12 sm:px-6 lg:grid-cols-[1fr_420px] lg:py-20">
      <div className="flex max-w-2xl flex-col justify-center">
        <p className="mb-3 text-sm font-semibold uppercase tracking-wide text-sage">Welcome back</p>
        <h1 className="text-4xl font-bold leading-tight text-ink sm:text-5xl">Return to your coding path.</h1>
        <p className="mt-5 text-lg leading-8 text-ink/68">
          Sign in to pick up your mentor sessions, saved exercises, and progress snapshot.
        </p>
      </div>
      <form onSubmit={handleSubmit} className="rounded border border-ink/10 bg-white p-6 shadow-soft">
        <h2 className="text-2xl font-semibold">Log in</h2>
        <label className="mt-6 block text-sm font-medium" htmlFor="email">
          Email
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="mt-2 w-full rounded border border-ink/15 px-3 py-2 outline-none focus:border-sage"
          required
        />
        <label className="mt-4 block text-sm font-medium" htmlFor="password">
          Password
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="mt-2 w-full rounded border border-ink/15 px-3 py-2 outline-none focus:border-sage"
          minLength={8}
          required
        />
        {error ? <p className="mt-4 text-sm font-medium text-red-700">{error}</p> : null}
        <button
          type="submit"
          disabled={isSubmitting}
          className="mt-6 w-full rounded bg-ink px-4 py-3 font-semibold text-white hover:bg-ink/90 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? 'Signing in...' : 'Log in'}
        </button>
        <p className="mt-4 text-center text-sm text-ink/65">
          New here?{' '}
          <Link to="/signup" className="font-semibold text-sage">
            Create an account
          </Link>
        </p>
      </form>
    </section>
  );
}
