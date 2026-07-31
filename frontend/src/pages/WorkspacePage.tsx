import Editor from '@monaco-editor/react';
import { Bug, Gauge, Lightbulb, Play, Save, Sparkles, Wrench } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import {
  Language,
  MentorAction,
  MentorResult,
  ExecuteResult,
  askMentor,
  executeCode,
  getDraft,
  saveDraft,
} from '../api/client';
import { useAuth } from '../state/useAuth';

const STARTER_CODE: Record<Language, string> = {
  python: "print('Hello from AI Code Mentor')\n",
  java: 'public class Main {\n  public static void main(String[] args) {\n    System.out.println("Hello from AI Code Mentor");\n  }\n}\n',
  cpp: '#include <iostream>\n\nint main() {\n  std::cout << "Hello from AI Code Mentor" << std::endl;\n  return 0;\n}\n',
};

const MONACO_LANGUAGE: Record<Language, string> = {
  python: 'python',
  java: 'java',
  cpp: 'cpp',
};

const MONACO_PATH: Record<Language, string> = {
  python: 'workspace.py',
  java: 'Main.java',
  cpp: 'main.cpp',
};

const MENTOR_TABS: Array<{
  action: MentorAction;
  label: string;
  icon: typeof Sparkles;
}> = [
  { action: 'explain', label: 'Explain', icon: Sparkles },
  { action: 'hint', label: 'Hint', icon: Lightbulb },
  { action: 'detect-bugs', label: 'Bugs', icon: Bug },
  { action: 'complexity', label: 'Complexity', icon: Gauge },
  { action: 'optimize', label: 'Optimize', icon: Wrench },
];

type WorkspaceProblemSelection = {
  slug: string;
  title: string;
  description: string;
  starterCode?: Partial<Record<Language, string>>;
  language: Language;
  code: string;
  stdin: string;
};

function buildProblemStarter(language: Language, title: string) {
  if (language === 'cpp') {
    return `#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n  // TODO: solve ${title}\n  return 0;\n}\n`;
  }
  if (language === 'java') {
    return `import java.util.*;\n\npublic class Main {\n  public static void main(String[] args) {\n    // TODO: solve ${title}\n  }\n}\n`;
  }
  return `# TODO: solve ${title}\n`;
}

export default function WorkspacePage() {
  const { accessToken } = useAuth();
  const [language, setLanguage] = useState<Language>('python');
  const [theme, setTheme] = useState<'vs-dark' | 'light'>('vs-dark');
  const [code, setCode] = useState(STARTER_CODE.python);
  const [stdin, setStdin] = useState('');
  const [activeProblem, setActiveProblem] = useState<WorkspaceProblemSelection | null>(null);
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [result, setResult] = useState<ExecuteResult | null>(null);
  const [runError, setRunError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [mentorAction, setMentorAction] = useState<MentorAction>('explain');
  const [hintLevel, setHintLevel] = useState<1 | 2 | 3 | 4>(1);
  const [problemStatement, setProblemStatement] = useState('');
  const [mentorResults, setMentorResults] = useState<Partial<Record<MentorAction, MentorResult>>>(
    {},
  );
  const [mentorError, setMentorError] = useState<string | null>(null);
  const [isAskingMentor, setIsAskingMentor] = useState(false);
  const loadedLanguage = useRef<Language>('python');

  const executionEnabled = true;
  const canRun = executionEnabled;
  const mentorResult = mentorResults[mentorAction] ?? null;
const statusLabel = useMemo(() => {
    if (saveState === 'saving') return 'Saving';
    if (saveState === 'saved') return 'Saved';
    if (saveState === 'error') return 'Save failed';
    return 'Ready';
  }, [saveState]);

  function getProblemStarter(problem: WorkspaceProblemSelection, nextLanguage: Language) {
    return problem.starterCode?.[nextLanguage] ?? buildProblemStarter(nextLanguage, problem.title);
  }

  useEffect(() => {
    setResult(null);
    setRunError(null);
  }, [accessToken, code, language, stdin]);

  useEffect(() => {
    setMentorResults({});
    setMentorError(null);
  }, [accessToken, code, language, problemStatement, result, stdin]);

  useEffect(() => {
    const rawSelection = localStorage.getItem('ai-code-mentor.workspace.problem');
    if (!rawSelection) return;
    localStorage.removeItem('ai-code-mentor.workspace.problem');

    try {
      const selection = JSON.parse(rawSelection) as WorkspaceProblemSelection;
      setActiveProblem(selection);
      setLanguage(selection.language);
      setCode(selection.code);
      setStdin(selection.stdin);
      setProblemStatement(`${selection.title}\n\n${selection.description}`);
      loadedLanguage.current = selection.language;
      setSaveState('idle');
    } catch {
      localStorage.removeItem('ai-code-mentor.workspace.problem');
    }
  }, []);

  useEffect(() => {
    if (!accessToken) return;

    let cancelled = false;
    loadedLanguage.current = language;
    setSaveState('idle');
    setResult(null);
    setRunError(null);

    if (activeProblem) {
      const starterCode = getProblemStarter(activeProblem, language);
      setCode(starterCode);
      setActiveProblem((current) =>
        current && (current.language !== language || current.code !== starterCode)
          ? {
              ...current,
              language,
              code: starterCode,
            }
          : current,
      );
      setSaveState('idle');
      return;
    }

    async function loadDraft() {
      try {
        const draft = await getDraft(accessToken!, language);
        if (!cancelled) {
          setCode((currentCode) => {
            if (activeProblem?.language === language && currentCode === activeProblem.code) {
              return currentCode;
            }
            return draft?.code ?? STARTER_CODE[language];
          });
          setSaveState(draft ? 'saved' : 'idle');
        }
      } catch {
        if (!cancelled) {
          setCode(STARTER_CODE[language]);
          setSaveState('idle');
        }
      }
    }

    loadDraft();
    return () => {
      cancelled = true;
    };
  }, [accessToken, activeProblem, language]);

  useEffect(() => {
    if (!accessToken || loadedLanguage.current !== language) return;

    setSaveState('saving');
    const timeoutId = window.setTimeout(async () => {
      try {
        await saveDraft(accessToken, { language, code });
        setSaveState('saved');
      } catch {
        setSaveState('error');
      }
    }, 650);

    return () => window.clearTimeout(timeoutId);
  }, [accessToken, code, language]);

  async function runCode() {
    if (!accessToken || !canRun) return;
    setIsRunning(true);
    setRunError(null);
    setResult(null);
    try {
      const output = await executeCode(accessToken, { language, code, stdin });
      setResult(output);
    } catch (err) {
      setRunError(err instanceof Error ? err.message : 'Unable to execute code');
    } finally {
      setIsRunning(false);
    }
  }

  async function askActiveMentor() {
    if (!accessToken) return;
    setIsAskingMentor(true);
    setMentorError(null);
    try {
      const output = await askMentor(accessToken, mentorAction, {
        language,
        code,
        problem_statement: problemStatement || undefined,
        hint_level: mentorAction === 'hint' ? hintLevel : undefined,
        stdin: stdin || undefined,
        stdout: result?.stdout || undefined,
        stderr: result?.stderr || undefined,
        exit_code: result?.exit_code,
      });
      setMentorResults((current) => ({ ...current, [mentorAction]: output }));
    } catch (err) {
      setMentorError(err instanceof Error ? err.message : 'Unable to reach the mentor');
    } finally {
      setIsAskingMentor(false);
    }
  }

  return (
    <section className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-6 sm:px-6">
      <div className="flex flex-col gap-3 border-b border-ink/10 pb-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink">Coding Workspace</h1>
          <p className="mt-1 text-sm text-ink/60">
            {activeProblem ? `${activeProblem.title} - ${statusLabel}` : statusLabel}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={language}
            onChange={(event) => setLanguage(event.target.value as Language)}
            className="rounded border border-ink/15 bg-white px-3 py-2 text-sm font-medium"
          >
            <option value="python">Python</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
          </select>
          <button
            type="button"
            onClick={() => setTheme((current) => (current === 'vs-dark' ? 'light' : 'vs-dark'))}
            className="rounded border border-ink/15 bg-white px-3 py-2 text-sm font-medium"
          >
            {theme === 'vs-dark' ? 'Dark' : 'Light'}
          </button>
          <div className="flex items-center gap-2 rounded border border-ink/10 bg-white px-3 py-2 text-sm text-ink/65">
            <Save aria-hidden="true" size={16} />
            {statusLabel}
          </div>
          <button
            type="button"
            onClick={runCode}
            disabled={!canRun || isRunning}
            title="Run code with Judge0"
            className="inline-flex items-center gap-2 rounded bg-coral px-4 py-2 text-sm font-semibold text-white hover:bg-coral/90 disabled:cursor-not-allowed disabled:opacity-55"
          >
            <Play aria-hidden="true" size={16} />
            {isRunning ? 'Running' : 'Run'}
          </button>
        </div>
      </div>

      <div className="grid min-h-[680px] gap-4 lg:grid-cols-[minmax(0,1fr)_420px]">
        <div className="overflow-hidden rounded border border-ink/10 bg-white">
          <Editor
            key={language}
            height="640px"
            language={MONACO_LANGUAGE[language]}
            path={MONACO_PATH[language]}
            theme={theme}
            value={code}
            onChange={(value) => setCode(value ?? '')}
            options={{
              minimap: { enabled: false },
              fontSize: 15,
              lineNumbersMinChars: 3,
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 2,
            }}
          />
        </div>

        <aside className="rounded border border-ink/10 bg-white p-4">
          <div className="flex items-center justify-between border-b border-ink/10 pb-3">
            <h2 className="text-base font-semibold">AI Mentor</h2>
            <span className="text-sm text-ink/55">
              {isAskingMentor ? 'thinking' : mentorResult?.source ?? 'local ready'}
            </span>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-2">
            {MENTOR_TABS.map((tab) => {
              const Icon = tab.icon;
              const active = mentorAction === tab.action;
              return (
                <button
                  type="button"
                  key={tab.action}
                  onClick={() => {
                    setMentorAction(tab.action);
                    setMentorError(null);
                  }}
                  className={`inline-flex items-center justify-center gap-2 rounded border px-3 py-2 text-sm font-semibold ${
                    active
                      ? 'border-sage bg-sage text-white'
                      : 'border-ink/10 bg-white text-ink hover:bg-paper'
                  }`}
                >
                  <Icon aria-hidden="true" size={16} />
                  {tab.label}
                </button>
              );
            })}
          </div>

          <label className="mt-4 block text-xs font-semibold uppercase tracking-wide text-ink/50">
            Problem context
          </label>
          <textarea
            value={problemStatement}
            onChange={(event) => setProblemStatement(event.target.value)}
            rows={4}
            className="mt-2 w-full resize-none rounded border border-ink/15 bg-white px-3 py-2 text-sm leading-6 outline-none focus:border-sage"
            placeholder="Optional prompt, constraints, or failing case"
          />

          {mentorAction === 'hint' ? (
            <div className="mt-4">
              <label className="block text-xs font-semibold uppercase tracking-wide text-ink/50">
                Hint level
              </label>
              <input
                type="range"
                min="1"
                max="4"
                value={hintLevel}
                onChange={(event) => setHintLevel(Number(event.target.value) as 1 | 2 | 3 | 4)}
                className="mt-3 w-full accent-coral"
              />
              <div className="mt-1 flex justify-between text-xs font-medium text-ink/50">
                <span>1</span>
                <span>2</span>
                <span>3</span>
                <span>4</span>
              </div>
            </div>
          ) : null}

          <button
            type="button"
            onClick={askActiveMentor}
            disabled={isAskingMentor}
            className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded bg-coral px-4 py-2 text-sm font-semibold text-white hover:bg-coral/90 disabled:cursor-not-allowed disabled:opacity-55"
          >
            <Sparkles aria-hidden="true" size={16} />
            {isAskingMentor ? 'Thinking' : 'Ask mentor'}
          </button>

          {mentorError ? <p className="mt-4 text-sm font-medium text-red-700">{mentorError}</p> : null}

          <div className="mt-4 min-h-56 overflow-auto rounded bg-ink p-4 text-sm leading-6 text-white">
            {mentorResult?.result ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{mentorResult.result}</ReactMarkdown>
            ) : (
              <p className="text-white/60">
                Choose a mentor tab, add optional problem context, then ask for guidance.
              </p>
            )}
          </div>

          <div className="mt-5 border-t border-ink/10 pt-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold">Run Output</h3>
              <span className="text-sm text-ink/55">
                {result ? `Exit ${result.exit_code}` : executionEnabled ? 'Ready' : 'Paused'}
              </span>
            </div>

            <label className="mt-3 block text-xs font-semibold uppercase tracking-wide text-ink/50">
              stdin
            </label>
            <textarea
              value={stdin}
              onChange={(event) => setStdin(event.target.value)}
              rows={3}
              className="mt-2 w-full resize-none rounded border border-ink/15 bg-white px-3 py-2 text-sm leading-6 outline-none focus:border-sage"
              placeholder="Optional input for your program"
            />

            {runError ? <p className="mt-3 text-sm font-medium text-red-700">{runError}</p> : null}

            <div className="mt-3 grid gap-3">
              <pre className="min-h-24 overflow-auto rounded bg-[#22352c] p-3 text-sm leading-6 text-white">
                {result?.stdout || ''}
              </pre>
              <pre className="min-h-24 overflow-auto rounded bg-[#3a1f2a] p-3 text-sm leading-6 text-white">
                {result?.stderr || ''}
              </pre>
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}
