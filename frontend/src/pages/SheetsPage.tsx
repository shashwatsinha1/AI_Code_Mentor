import { Layers } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { SheetListItem, getSheets } from '../api/client';
import { useAuth } from '../state/useAuth';

export default function SheetsPage() {
  const { accessToken } = useAuth();
  const [sheets, setSheets] = useState<SheetListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    getSheets(accessToken)
      .then((items) => {
        if (!cancelled) setSheets(items);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load pattern sheets');
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [accessToken]);

  return (
    <section className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <div className="border-b border-ink/10 pb-5">
        <h1 className="text-3xl font-bold text-ink">Curated Pattern Sheets</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-ink/65">
          Master interview questions categorized by core algorithmic patterns (Two Pointers, Sliding Window, Monotonic Stack, DP, Graphs) rather than raw topics. Track your solve progress with interactive checkboxes.
        </p>
      </div>

      {error ? <p className="mt-6 text-sm font-medium text-red-700">{error}</p> : null}
      {isLoading ? <p className="mt-6 text-sm text-ink/60">Loading pattern sheets...</p> : null}

      <div className="mt-6 grid gap-6 md:grid-cols-2">
        {sheets.map((sheet) => {
          const percent =
            sheet.total_questions > 0
              ? Math.round((sheet.completed_questions / sheet.total_questions) * 100)
              : 0;

          return (
            <Link
              key={sheet.slug}
              to={`/sheets/${sheet.slug}`}
              className="flex flex-col justify-between rounded-lg border border-ink/10 bg-white p-6 shadow-sm transition hover:border-sage hover:shadow-md"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="inline-flex items-center gap-1.5 rounded bg-sage/10 px-2.5 py-1 text-xs font-semibold text-sage">
                    <Layers size={14} />
                    Pattern-Wise
                  </span>
                  <span className="text-xs text-ink/50">By {sheet.author}</span>
                </div>
                <h2 className="mt-3 text-xl font-bold text-ink">{sheet.title}</h2>
                <p className="mt-2 text-sm leading-6 text-ink/70">{sheet.description}</p>
              </div>

              <div className="mt-6 border-t border-ink/10 pt-4">
                <div className="flex items-center justify-between text-xs font-semibold">
                  <span className="text-ink/60">Progress</span>
                  <span className="text-ink/80">
                    {sheet.completed_questions} / {sheet.total_questions} Solved ({percent}%)
                  </span>
                </div>
                <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-paper">
                  <div
                    className="h-full bg-sage transition-all duration-300"
                    style={{ width: `${percent}%` }}
                  />
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
