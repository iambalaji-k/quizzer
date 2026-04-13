"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import StatCard from "@/components/StatCard";
import { api } from "@/lib/api";
import { toPercent } from "@/lib/quiz-utils";

const DIFFICULTY_COLORS = {
  Easy: "#16a34a",
  Medium: "#ca8a04",
  Hard: "#dc2626"
};

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError("");
      try {
        const data = await api.getStats();
        setStats(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return <p className="text-sm text-slate-600">Loading dashboard...</p>;
  }

  if (error) {
    return <p className="text-sm text-red-600">{error}</p>;
  }

  const difficultyData = stats?.difficulty_wise_accuracy || [];
  const topicData = stats?.topic_wise_accuracy || [];
  const weakTopics = stats?.weak_topics || [];

  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-semibold">Performance Dashboard</h1>

      <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-4">
        <StatCard title="Total Questions" value={stats?.total_questions || 0} />
        <StatCard title="Total Attempted" value={stats?.total_attempted || 0} />
        <StatCard title="Correct Attempts" value={stats?.total_correct || 0} />
        <StatCard title="Wrong Attempts" value={stats?.total_wrong || 0} />
        <StatCard title="Accuracy" value={toPercent(stats?.accuracy_percentage)} />
        <StatCard title="Unattempted Questions" value={stats?.unattempted_questions || 0} />
        <StatCard
          title="Marked For Review"
          value={stats?.marked_for_review_count || 0}
        />
        <StatCard
          title="Coverage"
          value={`${stats?.attempted_subjects_count || 0} S / ${stats?.attempted_chapters_count || 0} C / ${stats?.attempted_topics_count || 0} T`}
          subtitle="Subjects / Chapters / Topics attempted"
        />
        <StatCard
          title="Weak Topics"
          value={weakTopics.length}
          subtitle="Bottom accuracy topics"
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card p-4">
          <h2 className="mb-3 text-base font-semibold">Difficulty-wise Accuracy</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={difficultyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="difficulty" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="accuracy">
                  {difficultyData.map((entry) => (
                    <Cell
                      key={entry.difficulty}
                      fill={DIFFICULTY_COLORS[entry.difficulty] || "#64748b"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-4">
          <h2 className="mb-3 text-base font-semibold">Topic-wise Accuracy</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={topicData} dataKey="attempted" nameKey="topic_name" outerRadius={95} label>
                  {topicData.map((entry, index) => (
                    <Cell
                      key={entry.topic_id}
                      fill={["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed"][index % 5]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="card p-4">
        <h2 className="mb-3 text-base font-semibold">Weak Topics</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left">
                <th className="px-2 py-2">Subject</th>
                <th className="px-2 py-2">Chapter</th>
                <th className="px-2 py-2">Topic</th>
                <th className="px-2 py-2">Attempted</th>
                <th className="px-2 py-2">Correct</th>
                <th className="px-2 py-2">Accuracy</th>
              </tr>
            </thead>
            <tbody>
              {weakTopics.map((topic) => (
                <tr key={topic.topic_id} className="border-b border-slate-100">
                  <td className="px-2 py-2">{topic.subject_name}</td>
                  <td className="px-2 py-2">{topic.chapter_name}</td>
                  <td className="px-2 py-2">{topic.topic_name}</td>
                  <td className="px-2 py-2">{topic.attempted}</td>
                  <td className="px-2 py-2">{topic.correct}</td>
                  <td className="px-2 py-2">{toPercent(topic.accuracy)}</td>
                </tr>
              ))}
              {!weakTopics.length && (
                <tr>
                  <td className="px-2 py-3 text-slate-500" colSpan={6}>
                    No attempts yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
