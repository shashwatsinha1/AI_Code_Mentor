import { Search } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

import { Difficulty, ProblemListItem, getProblems } from '../api/client';
import { useAuth } from '../state/useAuth';

const DIFFICULTIES: Array<Difficulty | ''> = ['', 'easy', 'medium', 'hard'];

function difficultyClass(difficulty: Difficulty) {
  if (difficulty === 'easy') return 'bg-sage/10 text-sage';
  if (difficulty === 'medium') return 'bg-coral/10 text-coral';
  return 'bg-ink/10 text-ink';
}

export default function ProblemsPage() {
  const { accessToken } = useAuth();
  const [problems, setProblems] = useState<ProblemListItem[]>([]);
  const [difficulty, setDifficulty] = useState<Difficulty | ''>('');
  const [tag, setTag] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    getProblems(accessToken, { difficulty, tag })
      .then((items) => {
        if (!cancelled) setProblems(items);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load problems');
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [accessToken, difficulty, tag]);

  const tagOptions = useMemo(() => {
    const tags = new Set<string>();
    problems.forEach((problem) => problem.tags.forEach((item) => tags.add(item)));
    return Array.from(tags).sort();
  }, [problems]);

  return (
    <section className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <div className="flex flex-col gap-4 border-b border-ink/10 pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-ink">Problem Bank</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-ink/65">
            Browse practice problems, inspect sample tests, and send starter code into the workspace.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={difficulty}
            onChange={(event) => setDifficulty(event.target.value as Difficulty | '')}
            className="rounded border border-ink/15 bg-white px-3 py-2 text-sm font-medium"
          >
            {DIFFICULTIES.map((item) => (
              <option key={item || 'all'} value={item}>
                {item ? item[0].toUpperCase() + item.slice(1) : 'All difficulties'}
              </option>
            ))}
          </select>
          <div className="flex items-center gap-2 rounded border border-ink/15 bg-white px-3 py-2">
            <Search aria-hidden="true" size={16} className="text-ink/45" />
            <input
              value={tag}
              onChange={(event) => setTag(event.target.value)}
              list="problem-tags"
              placeholder="Filter tag"
              className="w-36 bg-transparent text-sm outline-none"
            />
            <datalist id="problem-tags">
              {tagOptions.map((item) => (
                <option key={item} value={item} />
              ))}
            </datalist>
          </div>
        </div>
      </div>

      {error ? <p className="mt-6 text-sm font-medium text-red-700">{error}</p> : null}
      {isLoading ? <p className="mt-6 text-sm text-ink/60">Loading problems...</p> : null}

      <div className="mt-6 grid gap-3">
        {problems.map((problem) => (
          <Link
            key={problem.slug}
            to={`/problems/${problem.slug}`}
            className="rounded border border-ink/10 bg-white p-4 hover:border-sage/60"
          >
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold text-ink">{problem.title}</h2>
                <div className="mt-2 flex flex-wrap gap-2">
                  {problem.tags.map((item) => (
                    <span key={item} className="rounded bg-paper px-2 py-1 text-xs text-ink/65">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
              <span
                className={`w-fit rounded px-3 py-1 text-xs font-bold uppercase ${difficultyClass(
                  problem.difficulty,
                )}`}
              >
                {problem.difficulty}
              </span>
            </div>
          </Link>
        ))}
      </div>

      {!isLoading && problems.length === 0 ? (
        <p className="mt-6 text-sm text-ink/60">No problems match those filters.</p>
      ) : null}
    </section>
  );
}
