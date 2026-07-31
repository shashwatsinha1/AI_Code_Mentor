const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export type User = {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
};

export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type Language = 'python' | 'java' | 'cpp';

export type Draft = {
  id: number;
  language: Language;
  code: string;
  updated_at: string;
};

export type ExecuteResult = {
  stdout: string;
  stderr: string;
  exit_code: number;
  timed_out: boolean;
};

export type MentorAction = 'explain' | 'hint' | 'detect-bugs' | 'complexity' | 'optimize';

export type MentorResult = {
  result: string;
  source: 'openai' | 'local';
};

export type Difficulty = 'easy' | 'medium' | 'hard';

export type TestCase = {
  id: number;
  position: number;
  stdin: string;
  expected_stdout: string;
  is_sample: boolean;
};

export type ProblemListItem = {
  id: number;
  slug: string;
  title: string;
  difficulty: Difficulty;
  tags: string[];
  created_at: string;
};

export type Problem = ProblemListItem & {
  description: string;
  starter_code: Partial<Record<Language, string>>;
  test_cases: TestCase[];
};

function normalizeLanguage(language: string): Language {
  const normalized = language.trim().toLowerCase();
  if (normalized === 'c++' || normalized === 'cplusplus' || normalized === 'g++') {
    return 'cpp';
  }
  if (normalized === 'py' || normalized === 'python3') {
    return 'python';
  }
  if (normalized === 'java') {
    return 'java';
  }
  if (normalized === 'cpp' || normalized === 'python') {
    return normalized;
  }
  return 'python';
}

function formatApiError(payload: unknown): string {
  if (typeof payload === 'object' && payload !== null && 'detail' in payload) {
    const detail = (payload as { detail: unknown }).detail;
    if (typeof detail === 'string') {
      return detail;
    }
    return JSON.stringify(detail);
  }
  return 'Request failed';
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(formatApiError(payload));
  }

  return response.json() as Promise<T>;
}

export function signup(input: { email: string; password: string; full_name?: string }) {
  return request<User>('/auth/signup', {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export function login(input: { email: string; password: string }) {
  return request<TokenPair>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export function refreshToken(refresh_token: string) {
  return request<TokenPair>('/auth/refresh', {
    method: 'POST',
    body: JSON.stringify({ refresh_token }),
  });
}

export function getMe(accessToken: string) {
  return request<User>('/users/me', {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
}

export function getDraft(accessToken: string, language: Language) {
  return request<Draft | null>(`/drafts/${normalizeLanguage(language)}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
}

export function saveDraft(accessToken: string, input: { language: Language; code: string }) {
  return request<Draft>('/drafts', {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ ...input, language: normalizeLanguage(input.language) }),
  });
}

export function executeCode(
  accessToken: string,
  input: { language: Language; code: string; stdin?: string },
) {
  return request<ExecuteResult>('/execute', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ ...input, language: normalizeLanguage(input.language) }),
  });
}

export function askMentor(
  accessToken: string,
  action: MentorAction,
  input: {
    language: Language;
    code: string;
    problem_statement?: string;
    hint_level?: 1 | 2 | 3 | 4;
    stdin?: string;
    stdout?: string;
    stderr?: string;
    exit_code?: number;
  },
) {
  return request<MentorResult>(`/${action}`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ ...input, language: normalizeLanguage(input.language) }),
  });
}

export function getProblems(
  accessToken: string,
  filters: { difficulty?: Difficulty | ''; tag?: string } = {},
) {
  const params = new URLSearchParams();
  if (filters.difficulty) {
    params.set('difficulty', filters.difficulty);
  }
  if (filters.tag?.trim()) {
    params.set('tag', filters.tag.trim());
  }
  const query = params.toString();
  return request<ProblemListItem[]>(`/problems${query ? `?${query}` : ''}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
}

export function getProblem(accessToken: string, slug: string) {
  return request<Problem>(`/problems/${slug}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
}

export type TestCaseResultItem = {
  position: number;
  passed: boolean;
  is_sample: boolean;
  stdin: string;
  expected_stdout: string;
  actual_stdout: string;
  stderr: string;
  status_description: string;
};

export type SubmitCodeResponse = {
  submission_id: number;
  problem_slug: string;
  status: 'ACCEPTED' | 'WRONG_ANSWER' | 'TIME_LIMIT_EXCEEDED' | 'COMPILE_ERROR' | 'RUNTIME_ERROR';
  passed_test_cases: number;
  total_test_cases: number;
  runtime_ms?: number;
  test_results: TestCaseResultItem[];
};

export type TopicStat = {
  tag: string;
  attempted: number;
  solved: number;
  pass_rate: number;
};

export type RecentSubmissionItem = {
  id: number;
  problem_slug: string;
  problem_title: string;
  difficulty: string;
  language: string;
  status: string;
  passed_test_cases: number;
  total_test_cases: number;
  created_at: string;
};

export type UserAnalyticsResponse = {
  total_solved: number;
  solved_by_difficulty: {
    easy: number;
    medium: number;
    hard: number;
  };
  total_submissions: number;
  accuracy_rate: number;
  topic_stats: TopicStat[];
  weak_topics: string[];
  recent_submissions: RecentSubmissionItem[];
};

export function submitProblemCode(
  accessToken: string,
  slug: string,
  input: { language: Language; code: string },
) {
  return request<SubmitCodeResponse>(`/problems/${slug}/submit`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ ...input, language: normalizeLanguage(input.language) }),
  });
}

export function getUserAnalytics(accessToken: string) {
  return request<UserAnalyticsResponse>('/users/me/analytics', {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
}

export type SheetListItem = {
  id: number;
  slug: string;
  title: string;
  description: string;
  author: string;
  total_questions: number;
  completed_questions: number;
};

export type SheetItemRead = {
  id: number;
  pattern: string;
  position: number;
  title: string;
  difficulty: Difficulty;
  platform: string;
  problem_url: string;
  article_url?: string;
  problem_slug?: string;
  description?: string;
  is_completed: boolean;
};

export type PatternSection = {
  pattern: string;
  total_count: number;
  completed_count: number;
  items: SheetItemRead[];
};

export type SheetDetailResponse = {
  id: number;
  slug: string;
  title: string;
  description: string;
  author: string;
  total_questions: number;
  completed_questions: number;
  patterns: PatternSection[];
};

export type ToggleProgressResponse = {
  item_id: number;
  is_completed: boolean;
  completed_questions: number;
  total_questions: number;
};

export function getSheets(accessToken: string) {
  return request<SheetListItem[]>('/sheets', {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
}

export function getSheetDetail(accessToken: string, slug: string) {
  return request<SheetDetailResponse>(`/sheets/${slug}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
}

export function toggleSheetItem(accessToken: string, slug: string, itemId: number) {
  return request<ToggleProgressResponse>(`/sheets/${slug}/items/${itemId}/toggle`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
}
