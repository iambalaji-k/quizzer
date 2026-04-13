"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { difficultyBadgeClass } from "@/lib/quiz-utils";

export default function ReviewPage() {
  const [attempts, setAttempts] = useState([]);
  const [wrongOnly, setWrongOnly] = useState(false);
  const [markedOnly, setMarkedOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadAttempts();
  }, [wrongOnly, markedOnly]);

  async function loadAttempts() {
    setLoading(true);
    setError("");
    try {
      const params = {
        wrong_only: wrongOnly || undefined,
        marked_for_review: markedOnly || undefined
      };
      const data = await api.getAttempts(params);
      setAttempts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-5">
      <h1 className="text-2xl font-semibold">Attempt Review</h1>

      <div className="card flex flex-wrap gap-4 p-4 text-sm">
        <label className="inline-flex items-center gap-2">
          <input
            type="checkbox"
            checked={wrongOnly}
            onChange={(e) => setWrongOnly(e.target.checked)}
          />
          Show only wrong attempts
        </label>
        <label className="inline-flex items-center gap-2">
          <input
            type="checkbox"
            checked={markedOnly}
            onChange={(e) => setMarkedOnly(e.target.checked)}
          />
          Show only marked for review
        </label>
      </div>

      {loading ? <p className="text-sm text-slate-600">Loading attempts...</p> : null}
      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <div className="space-y-3">
        {attempts.map((attempt) => (
          <article key={attempt.attempt_id} className="card p-4">
            <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
              <span
                className={`rounded-full px-2 py-1 text-xs font-semibold ${difficultyBadgeClass(
                  attempt.difficulty
                )}`}
              >
                {attempt.difficulty}
              </span>
              <p className="text-xs text-slate-500">{new Date(attempt.timestamp).toLocaleString()}</p>
            </div>

            <h2 className="text-base font-semibold">{attempt.question_text}</h2>
            <p className="mt-2 text-sm text-slate-700">
              Selected:{" "}
              <span className={attempt.is_correct ? "text-green-700" : "text-red-700"}>
                {attempt.selected_option_text}
              </span>
            </p>
            <p className="text-sm text-slate-700">
              Correct: <span className="text-green-700">{attempt.correct_option_text}</span>
            </p>
            <p className="mt-2 text-sm text-slate-600">{attempt.explanation}</p>
          </article>
        ))}
      </div>

      {!loading && !attempts.length ? (
        <p className="text-sm text-slate-600">No attempts found for selected filters.</p>
      ) : null}
    </section>
  );
}

