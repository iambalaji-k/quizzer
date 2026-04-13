"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export default function ImportPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleUpload(event) {
    event.preventDefault();
    if (!file) {
      setError("Please select a CSV or JSON file.");
      return;
    }
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const extension = file.name.split(".").pop()?.toLowerCase();
      const result =
        extension === "json" ? await api.importJson(file) : await api.importCsv(file);
      setMessage(
        `Import complete. Rows: ${result.total_rows}, Inserted: ${result.inserted_questions}, Failed: ${result.failed_rows}`
      );
      if (result.failures_log_path) {
        setMessage((prev) => `${prev}. Fail log: ${result.failures_log_path}`);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-5">
      <h1 className="text-2xl font-semibold">CSV / JSON Import</h1>

      <form onSubmit={handleUpload} className="card space-y-4 p-5">
        <p className="text-sm text-slate-600">
          Expected columns: subject, chapter, topic, difficulty, question, option1-4, answer, explanation.
        </p>
        <pre className="overflow-x-auto rounded-md bg-slate-100 p-3 text-xs text-slate-700">
{`JSON format:
{
  "questions": [
    {
      "subject": "Direct Tax Laws",
      "chapter": "Capital Gains",
      "topic": "Exemptions",
      "difficulty": "Easy",
      "question": "Sample question text",
      "options": ["A", "B", "C", "D"],
      "answer": 1,
      "explanation": "Sample explanation"
    }
  ]
}`}
        </pre>
        <input
          type="file"
          accept=".csv,.json"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
          className="block w-full rounded-md border border-slate-300 p-2 text-sm"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {loading ? "Uploading..." : "Upload File"}
        </button>
      </form>

      {message ? <p className="text-sm text-green-700">{message}</p> : null}
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
    </section>
  );
}
