import {
  ArrowLeft,
  BookOpen,
  CheckSquare,
  ChevronDown,
  ChevronRight,
  Code2,
  ExternalLink,
  Square,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import {
  Difficulty,
  SheetDetailResponse,
  getSheetDetail,
  toggleSheetItem,
} from '../api/client';
import { useAuth } from '../state/useAuth';

function platformBadge(platform: string) {
  if (platform === 'leetcode') return 'bg-amber-100 text-amber-900 border-amber-200';
  if (platform === 'codeforces') return 'bg-red-100 text-red-900 border-red-200';
  return 'bg-emerald-100 text-emerald-900 border-emerald-200';
}

function difficultyClass(difficulty: Difficulty) {
  if (difficulty === 'easy') return 'text-emerald-700 bg-emerald-50';
  if (difficulty === 'medium') return 'text-amber-700 bg-amber-50';
  return 'text-red-700 bg-red-50';
}

export default function SheetDetailPage() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { accessToken } = useAuth();
  const [sheet, setSheet] = useState<SheetDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedPatterns, setExpandedPatterns] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (!accessToken || !slug) return;
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    getSheetDetail(accessToken, slug)
      .then((res) => {
        if (!cancelled) {
          setSheet(res);
          // Expand all patterns by default
          const exp: Record<string, boolean> = {};
          res.patterns.forEach((p) => {
            exp[p.pattern] = true;
          });
          setExpandedPatterns(exp);
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load sheet');
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [accessToken, slug]);

  function togglePattern(patternName: string) {
    setExpandedPatterns((current) => ({
      ...current,
      [patternName]: !current[patternName],
    }));
  }

  async function handleToggleItem(itemId: number) {
    if (!accessToken || !slug || !sheet) return;

    // Optimistic UI update
    setSheet((prevSheet) => {
      if (!prevSheet) return prevSheet;
      let diff = 0;
      const updatedPatterns = prevSheet.patterns.map((pat) => {
        const updatedItems = pat.items.map((item) => {
          if (item.id === itemId) {
            const nextDone = !item.is_completed;
            diff = nextDone ? 1 : -1;
            return { ...item, is_completed: nextDone };
          }
          return item;
        });
        const patCompleted = updatedItems.filter((i) => i.is_completed).length;
        return { ...pat, completed_count: patCompleted, items: updatedItems };
      });

      return {
        ...prevSheet,
        completed_questions: Math.max(0, prevSheet.completed_questions + diff),
        patterns: updatedPatterns,
      };
    });

    try {
      const res = await toggleSheetItem(accessToken, slug, itemId);
      setSheet((prevSheet) => (prevSheet ? { ...prevSheet, completed_questions: res.completed_questions } : prevSheet));
    } catch {
      // Refresh on error
      getSheetDetail(accessToken, slug).then(setSheet).catch(() => {});
    }
  }

  function openInWorkspace(problemSlug?: string, title?: string, description?: string) {
    if (!problemSlug) return;
    localStorage.setItem(
      'ai-code-mentor.workspace.problem',
      JSON.stringify({
        slug: problemSlug,
        title: title || problemSlug,
        description: description || '',
        language: 'python',
        code: `# TODO: solve ${title || problemSlug}\n`,
        stdin: '',
      }),
    );
    navigate('/workspace');
  }

  if (isLoading) {
    return <p className="mx-auto max-w-6xl px-4 py-8 text-sm text-ink/60">Loading pattern sheet...</p>;
  }

  if (error || !sheet) {
    return (
      <section className="mx-auto max-w-6xl px-4 py-8">
        <Link to="/sheets" className="inline-flex items-center gap-2 text-sm font-semibold text-sage">
          <ArrowLeft aria-hidden="true" size={16} />
          Pattern Sheets
        </Link>
        <p className="mt-6 text-sm font-medium text-red-700">{error ?? 'Sheet not found'}</p>
      </section>
    );
  }

  const overallPercent =
    sheet.total_questions > 0
      ? Math.round((sheet.completed_questions / sheet.total_questions) * 100)
      : 0;

  return (
    <section className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <Link to="/sheets" className="inline-flex items-center gap-2 text-sm font-semibold text-sage">
        <ArrowLeft aria-hidden="true" size={16} />
        Pattern Sheets
      </Link>

      <div className="mt-4 border-b border-ink/10 pb-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-ink">{sheet.title}</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-ink/65">{sheet.description}</p>
          </div>
          <div className="w-full min-w-48 rounded-lg border border-ink/10 bg-white p-4 md:w-auto">
            <div className="flex justify-between text-xs font-semibold">
              <span>Overall Progress</span>
              <span className="text-sage font-bold">
                {sheet.completed_questions} / {sheet.total_questions} ({overallPercent}%)
              </span>
            </div>
            <div className="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-paper">
              <div
                className="h-full bg-sage transition-all duration-300"
                style={{ width: `${overallPercent}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Pattern-Wise Accordions */}
      <div className="mt-6 flex flex-col gap-4">
        {sheet.patterns.map((section) => {
          const isExpanded = expandedPatterns[section.pattern] ?? true;
          const patPercent =
            section.total_count > 0
              ? Math.round((section.completed_count / section.total_count) * 100)
              : 0;

          return (
            <div
              key={section.pattern}
              className="overflow-hidden rounded-lg border border-ink/10 bg-white shadow-sm"
            >
              {/* Pattern Header */}
              <div
                onClick={() => togglePattern(section.pattern)}
                className="flex cursor-pointer items-center justify-between bg-paper/60 px-5 py-4 transition hover:bg-paper"
              >
                <div className="flex items-center gap-3">
                  {isExpanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
                  <h2 className="text-lg font-bold text-ink">{section.pattern}</h2>
                  <span className="rounded-full bg-white px-3 py-0.5 text-xs font-semibold text-ink/70 border border-ink/10">
                    {section.completed_count} / {section.total_count} Solved
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="hidden sm:block w-32 h-2 overflow-hidden rounded-full bg-black/10">
                    <div
                      className="h-full bg-sage transition-all duration-300"
                      style={{ width: `${patPercent}%` }}
                    />
                  </div>
                  <span className="text-xs font-semibold text-ink/60">{patPercent}%</span>
                </div>
              </div>

              {/* Problem Rows */}
              {isExpanded ? (
                <div className="divide-y divide-ink/10">
                  {section.items.map((item) => (
                    <div
                      key={item.id}
                      className={`flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between transition ${
                        item.is_completed ? 'bg-emerald-50/40' : 'hover:bg-paper/30'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <button
                          type="button"
                          onClick={() => handleToggleItem(item.id)}
                          className="mt-0.5 text-sage transition hover:scale-110"
                          title={item.is_completed ? 'Mark unsolved' : 'Mark solved'}
                        >
                          {item.is_completed ? (
                            <CheckSquare size={22} className="fill-sage text-white" />
                          ) : (
                            <Square size={22} className="text-ink/30 hover:text-sage" />
                          )}
                        </button>
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <span
                              className={`text-base font-semibold ${
                                item.is_completed ? 'line-through text-ink/50' : 'text-ink'
                              }`}
                            >
                              {item.title}
                            </span>
                            <span
                              className={`rounded border px-2 py-0.5 text-[11px] font-bold uppercase ${platformBadge(
                                item.platform,
                              )}`}
                            >
                              {item.platform}
                            </span>
                            <span
                              className={`rounded px-2 py-0.5 text-[11px] font-bold uppercase ${difficultyClass(
                                item.difficulty,
                              )}`}
                            >
                              {item.difficulty}
                            </span>
                          </div>
                          {item.description ? (
                            <p className="mt-1 text-xs text-ink/65">{item.description}</p>
                          ) : null}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 pl-9 sm:pl-0">
                        {item.article_url ? (
                          <a
                            href={item.article_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 rounded border border-ink/15 bg-white px-2.5 py-1.5 text-xs font-semibold text-ink/80 hover:bg-paper"
                            title="Read Striver / Editorial Article"
                          >
                            <BookOpen size={14} className="text-sage" />
                            Article
                          </a>
                        ) : null}

                        <a
                          href={item.problem_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 rounded border border-ink/15 bg-white px-2.5 py-1.5 text-xs font-semibold text-ink/80 hover:bg-paper"
                          title="Open on LeetCode / Codeforces / GFG"
                        >
                          <ExternalLink size={14} className="text-blue-600" />
                          Practice
                        </a>

                        {item.problem_slug ? (
                          <button
                            type="button"
                            onClick={() => openInWorkspace(item.problem_slug, item.title, item.description)}
                            className="inline-flex items-center gap-1 rounded bg-coral px-2.5 py-1.5 text-xs font-semibold text-white hover:bg-coral/90"
                            title="Solve in local IDE workspace"
                          >
                            <Code2 size={14} />
                            Workspace
                          </button>
                        ) : null}
                      </div>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </section>
  );
}
