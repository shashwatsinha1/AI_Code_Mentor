import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js';
import { Award, CheckCircle2, Clock, Target, AlertTriangle } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Bar, Doughnut } from 'react-chartjs-2';
import { Link } from 'react-router-dom';

import { UserAnalyticsResponse, getUserAnalytics } from '../api/client';
import { useAuth } from '../state/useAuth';

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend);

export default function ProgressPage() {
  const { accessToken } = useAuth();
  const [data, setData] = useState<UserAnalyticsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    getUserAnalytics(accessToken)
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Unable to load analytics');
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [accessToken]);

  if (isLoading) {
    return <p className="mx-auto max-w-6xl px-4 py-8 text-sm text-ink/60">Loading analytics...</p>;
  }

  if (error || !data) {
    return (
      <section className="mx-auto max-w-6xl px-4 py-8">
        <p className="text-sm font-medium text-red-700">{error ?? 'Unable to display analytics'}</p>
      </section>
    );
  }

  const doughnutData = {
    labels: ['Easy', 'Medium', 'Hard'],
    datasets: [
      {
        data: [
          data.solved_by_difficulty.easy,
          data.solved_by_difficulty.medium,
          data.solved_by_difficulty.hard,
        ],
        backgroundColor: ['#22c55e', '#f97316', '#ef4444'],
        borderWidth: 2,
        borderColor: '#ffffff',
      },
    ],
  };

  const topicLabels = data.topic_stats.map((t) => t.tag);
  const topicPassRates = data.topic_stats.map((t) => t.pass_rate);

  const barData = {
    labels: topicLabels.length ? topicLabels : ['No data'],
    datasets: [
      {
        label: 'Accuracy %',
        data: topicPassRates.length ? topicPassRates : [0],
        backgroundColor: '#3b82f6',
        borderRadius: 4,
      },
    ],
  };

  return (
    <section className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <div className="border-b border-ink/10 pb-5">
        <h1 className="text-3xl font-bold text-ink">Progress & Analytics</h1>
        <p className="mt-2 text-sm text-ink/65">
          Track your problem-solving metrics, accuracy rates, and weak topics over time.
        </p>
      </div>

      {/* Top Metric Cards */}
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded border border-ink/10 bg-white p-5">
          <div className="flex items-center gap-3">
            <CheckCircle2 size={24} className="text-emerald-600" />
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-ink/50">Solved</p>
              <p className="text-2xl font-bold text-ink">{data.total_solved}</p>
            </div>
          </div>
        </div>

        <div className="rounded border border-ink/10 bg-white p-5">
          <div className="flex items-center gap-3">
            <Target size={24} className="text-blue-600" />
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-ink/50">Accuracy</p>
              <p className="text-2xl font-bold text-ink">{data.accuracy_rate}%</p>
            </div>
          </div>
        </div>

        <div className="rounded border border-ink/10 bg-white p-5">
          <div className="flex items-center gap-3">
            <Clock size={24} className="text-purple-600" />
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-ink/50">Submissions</p>
              <p className="text-2xl font-bold text-ink">{data.total_submissions}</p>
            </div>
          </div>
        </div>

        <div className="rounded border border-ink/10 bg-white p-5">
          <div className="flex items-center gap-3">
            <Award size={24} className="text-amber-500" />
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-ink/50">Weak Topics</p>
              <p className="text-2xl font-bold text-ink">{data.weak_topics.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Weak Topics Warning Alert */}
      {data.weak_topics.length > 0 ? (
        <div className="mt-6 flex items-start gap-3 rounded border border-amber-300 bg-amber-50 p-4 text-amber-900">
          <AlertTriangle size={20} className="mt-0.5 shrink-0 text-amber-600" />
          <div>
            <h3 className="font-semibold text-sm">Recommended Revision Focus</h3>
            <p className="mt-1 text-xs leading-5">
              Based on your submission history, consider practicing more problems tagged with:{' '}
              <span className="font-bold">{data.weak_topics.join(', ')}</span>.
            </p>
          </div>
        </div>
      ) : null}

      {/* Charts Section */}
      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <div className="rounded border border-ink/10 bg-white p-5">
          <h2 className="text-base font-semibold text-ink">Problems Solved by Difficulty</h2>
          <div className="mt-4 flex justify-center h-64">
            <Doughnut data={doughnutData} options={{ maintainAspectRatio: false }} />
          </div>
        </div>

        <div className="rounded border border-ink/10 bg-white p-5">
          <h2 className="text-base font-semibold text-ink">Topic Accuracy %</h2>
          <div className="mt-4 flex justify-center h-64">
            <Bar data={barData} options={{ maintainAspectRatio: false }} />
          </div>
        </div>
      </div>

      {/* Recent Submissions History Table */}
      <div className="mt-8">
        <h2 className="text-lg font-semibold text-ink">Recent Submissions</h2>
        {data.recent_submissions.length === 0 ? (
          <p className="mt-3 text-sm text-ink/60">No submissions recorded yet. Start solving problems!</p>
        ) : (
          <div className="mt-3 overflow-x-auto rounded border border-ink/10 bg-white">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-ink/10 bg-paper text-xs uppercase tracking-wide text-ink/60">
                <tr>
                  <th className="px-4 py-3">Problem</th>
                  <th className="px-4 py-3">Language</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Test Cases</th>
                  <th className="px-4 py-3">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink/10">
                {data.recent_submissions.map((sub) => (
                  <tr key={sub.id} className="hover:bg-paper/50">
                    <td className="px-4 py-3 font-medium">
                      <Link to={`/problems/${sub.problem_slug}`} className="text-sage hover:underline">
                        {sub.problem_title}
                      </Link>
                    </td>
                    <td className="px-4 py-3 uppercase text-xs font-semibold text-ink/65">{sub.language}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`rounded px-2.5 py-1 text-xs font-bold ${
                          sub.status === 'ACCEPTED'
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {sub.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-ink/75">
                      {sub.passed_test_cases} / {sub.total_test_cases}
                    </td>
                    <td className="px-4 py-3 text-xs text-ink/55">
                      {new Date(sub.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
