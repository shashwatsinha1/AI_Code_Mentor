import Editor from '@monaco-editor/react';
import { ArrowLeft, CheckCircle2, Code2, Send, XCircle } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Link as RouterLink } from 'react-router-dom';

import {
  Language,
  Problem,
  SubmitCodeResponse,
  getProblem,
  submitProblemCode,
} from '../api/client';
import { useAuth } from '../state/useAuth';

const DEFAULT_LANGUAGE: Language = 'python';

function buildProblemStarter(language: Language, title: string) {
  if (language === 'cpp') {
    return `#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  // TODO: solve ${title}\n  return 0;\n}\n`;
  }
  if (language === 'java') {
    return `import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    // TODO: solve ${title}\n  }\n}\n`;
  }
  return `# TODO: solve ${title}\n`;
}

export default function ProblemDetailPage() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { accessToken } = useAuth();
  const [problem, setProblem] = useState<Problem | null>(null);
  const [language, setLanguage] = useState<Language>(DEFAULT_LANGUAGE);
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<SubmitCodeResponse | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken || !slug) return;
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    getProblem(accessToken, slug)
      .then((item) => {
        if (!cancelled) {
          setProblem(item);
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load problem');
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [accessToken, slug]);

  useEffect(() => {
    if (!problem) return;
    setCode(problem.starter_code[language] ?? buildProblemStarter(language, problem.title));
  }, [language, problem]);

  function openInWorkspace() {
    if (!problem) return;
    const starterCode = code || problem.starter_code[language] || buildProblemStarter(language, problem.title);
    localStorage.setItem(
      'ai-code-mentor.workspace.problem',
      JSON.stringify({
        slug: problem.slug,
        title: problem.title,
        description: problem.description,
        starterCode: problem.starter_code,
        language,
        code: starterCode,
        stdin: problem.test_cases[0]?.stdin ?? '',
      }),
    );
    navigate('/workspace');
  }

  async function handleSubmitCode() {
    if (!accessToken || !slug || !code.trim()) return;
    setIsSubmitting(true);
    setSubmitError(null);
    setSubmitResult(null);

    try {
      const res = await submitProblemCode(accessToken, slug, { language, code });
      setSubmitResult(res);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : 'Submission failed');
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoading) {
    return <p className="mx-auto max-w-6xl px-4 py-8 text-sm text-ink/60">Loading problem...</p>;
  }

  if (error || !problem) {
    return (
      <section className="mx-auto max-w-6xl px-4 py-8">
        <RouterLink to="/problems" className="inline-flex items-center gap-2 text-sm font-semibold text-sage">
          <ArrowLeft aria-hidden="true" size={16} />
          Problems
        </RouterLink>
        <p className="mt-6 text-sm font-medium text-red-700">{error ?? 'Problem not found'}</p>
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <RouterLink to="/problems" className="inline-flex items-center gap-2 text-sm font-semibold text-sage">
        <ArrowLeft aria-hidden="true" size={16} />
        Problems
      </RouterLink>

      <div className="mt-5 grid gap-6 lg:grid-cols-[minmax(0,1fr)_440px]">
        <article className="flex flex-col gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-3xl font-bold text-ink">{problem.title}</h1>
              <span className="rounded bg-paper px-3 py-1 text-xs font-bold uppercase text-ink/60">
                {problem.difficulty}
              </span>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {problem.tags.map((tag) => (
                <span key={tag} className="rounded bg-white px-2 py-1 text-xs text-ink/65 border border-ink/10">
                  {tag}
                </span>
              ))}
            </div>
            <p className="mt-6 whitespace-pre-wrap text-base leading-8 text-ink/75">
              {problem.description}
            </p>
          </div>

          <h2 className="mt-4 text-lg font-semibold text-ink">Sample Cases</h2>
          <div className="grid gap-3">
            {problem.test_cases.map((testCase) => (
              <div key={testCase.id} className="rounded border border-ink/10 bg-white p-4">
                <p className="text-sm font-semibold text-ink">Case {testCase.position}</p>
                <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-ink/50">stdin</p>
                <pre className="mt-2 overflow-auto rounded bg-ink p-3 text-sm text-white">
                  {testCase.stdin}
                </pre>
                <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-ink/50">
                  expected stdout
                </p>
                <pre className="mt-2 overflow-auto rounded bg-[#22352c] p-3 text-sm text-white">
                  {testCase.expected_stdout}
                </pre>
              </div>
            ))}
          </div>
        </article>

        {/* Code Editor & Test Evaluator Panel */}
        <aside className="flex flex-col gap-4 rounded border border-ink/10 bg-white p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold text-ink">Code Solution</h2>
            <select
              value={language}
              onChange={(event) => setLanguage(event.target.value as Language)}
              className="rounded border border-ink/15 bg-white px-3 py-1.5 text-sm font-medium"
            >
              <option value="python">Python</option>
              <option value="cpp">C++</option>
              <option value="java">Java</option>
            </select>
          </div>

          <div className="overflow-hidden rounded border border-ink/10 bg-white">
            <Editor
              height="320px"
              language={language === 'cpp' ? 'cpp' : language}
              theme="vs-dark"
              value={code}
              onChange={(val) => setCode(val ?? '')}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbersMinChars: 3,
                scrollBeyondLastLine: false,
                automaticLayout: true,
              }}
            />
          </div>

          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleSubmitCode}
              disabled={isSubmitting || !code.trim()}
              className="inline-flex flex-1 items-center justify-center gap-2 rounded bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
            >
              <Send aria-hidden="true" size={16} />
              {isSubmitting ? 'Evaluating...' : 'Submit Code'}
            </button>
            <button
              type="button"
              onClick={openInWorkspace}
              className="inline-flex items-center justify-center gap-2 rounded border border-ink/15 bg-white px-4 py-2.5 text-sm font-semibold text-ink hover:bg-paper"
            >
              <Code2 aria-hidden="true" size={16} />
              Workspace
            </button>
          </div>

          {submitError ? <p className="text-sm font-medium text-red-700">{submitError}</p> : null}

          {/* Test Case Results Output */}
          {submitResult ? (
            <div className="mt-2 rounded border border-ink/10 bg-paper p-4">
              <div className="flex items-center justify-between border-b border-ink/10 pb-3">
                <div className="flex items-center gap-2">
                  {submitResult.status === 'ACCEPTED' ? (
                    <CheckCircle2 className="text-emerald-600" size={20} />
                  ) : (
                    <XCircle className="text-red-600" size={20} />
                  )}
                  <span
                    className={`text-sm font-bold ${
                      submitResult.status === 'ACCEPTED' ? 'text-emerald-800' : 'text-red-800'
                    }`}
                  >
                    {submitResult.status}
                  </span>
                </div>
                <span className="text-xs font-semibold text-ink/65">
                  {submitResult.passed_test_cases} / {submitResult.total_test_cases} passed
                </span>
              </div>

              <div className="mt-3 space-y-2 max-h-48 overflow-auto">
                {submitResult.test_results.map((tr) => (
                  <div
                    key={tr.position}
                    className={`rounded border p-2.5 text-xs ${
                      tr.passed
                        ? 'border-emerald-200 bg-emerald-50 text-emerald-950'
                        : 'border-red-200 bg-red-50 text-red-950'
                    }`}
                  >
                    <div className="flex justify-between font-semibold">
                      <span>Test Case #{tr.position}</span>
                      <span>{tr.status_description}</span>
                    </div>
                    {!tr.passed ? (
                      <div className="mt-2 space-y-1 font-mono text-[11px]">
                        <p>Expected: {tr.expected_stdout}</p>
                        <p>Received: {tr.actual_stdout || '(empty)'}</p>
                        {tr.stderr ? <p className="text-red-700">Stderr: {tr.stderr}</p> : null}
                      </div>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </aside>
      </div>
    </section>
  );
}
