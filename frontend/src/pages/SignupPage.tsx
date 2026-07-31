import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { signup } from '../api/client';
import { useAuth } from '../state/useAuth';

export default function SignupPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await signup({ email, password, full_name: fullName || undefined });
      await login(email, password);
      navigate('/profile');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create account');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="mx-auto grid max-w-6xl gap-8 px-4 py-12 sm:px-6 lg:grid-cols-[1fr_420px] lg:py-20">
      <div className="flex max-w-2xl flex-col justify-center">
        <p className="mb-3 text-sm font-semibold uppercase tracking-wide text-coral">Start learning</p>
        <h1 className="text-4xl font-bold leading-tight text-ink sm:text-5xl">Build your AI code mentor account.</h1>
        <p className="mt-5 text-lg leading-8 text-ink/68">
          Phase one keeps the doorway simple: create an account, sign in, and verify protected profile access.
        </p>
      </div>
      <form onSubmit={handleSubmit} className="rounded border border-ink/10 bg-white p-6 shadow-soft">
        <h2 className="text-2xl font-semibold">Sign up</h2>
        <label className="mt-6 block text-sm font-medium" htmlFor="name">
          Full name
        </label>
        <input
          id="name"
          value={fullName}
          onChange={(event) => setFullName(event.target.value)}
          className="mt-2 w-full rounded border border-ink/15 px-3 py-2 outline-none focus:border-sage"
        />
        <label className="mt-4 block text-sm font-medium" htmlFor="email">
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
          {isSubmitting ? 'Creating account...' : 'Create account'}
        </button>
        <p className="mt-4 text-center text-sm text-ink/65">
          Already registered?{' '}
          <Link to="/login" className="font-semibold text-sage">
            Log in
          </Link>
        </p>
      </form>
    </section>
  );
}
