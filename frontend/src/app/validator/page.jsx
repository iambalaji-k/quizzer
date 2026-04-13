"use client";

import { useState } from "react";
import { api } from "@/lib/api";

const TABS = [
  { id: "csv", label: "CSV Validator" },
  { id: "json", label: "JSON Validator" }
];

export default function ValidatorPage() {
  const [tab, setTab] = useState("csv");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function handleValidate(event) {
    event.preventDefault();
    if (!file) {
      setError(`Please select a ${tab.toUpperCase()} file.`);
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const nextResult = tab === "csv" ? await api.validateCsv(file) : await api.validateJson(file);
      setResult(nextResult);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-5">
      <div>
        <h1 className="text-2xl font-semibold">File Validator</h1>
        <p className="mt-1 text-sm text-slate-600">
          Validate CSV or JSON before upload and review row-level errors in the browser.
        </p>
      </div>

      <div className="card p-4">
        <div className="mb-4 flex gap-2">
          {TABS.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => {
                setTab(item.id);
                setFile(null);
                setError("");
                setResult(null);
              }}
              className={`rounded-md px-3 py-2 text-sm font-medium ${
                tab === item.id
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleValidate} className="space-y-4">
          <input
            type="file"
            accept={tab === "csv" ? ".csv" : ".json"}
            onChange={(event) => setFile(event.target.files?.[0] || null)}
            className="block w-full rounded-md border border-slate-300 p-2 text-sm"
          />

          <button
            type="submit"
            disabled={loading}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {loading ? "Validating..." : `Validate ${tab.toUpperCase()}`}
          </button>
        </form>
      </div>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      {result ? (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-4">
            <div className="card p-4">
              <p className="text-sm text-slate-500">File Type</p>
              <p className="mt-2 text-lg font-semibold uppercase">{result.file_type}</p>
            </div>
            <div className="card p-4">
              <p className="text-sm text-slate-500">Rows Checked</p>
              <p className="mt-2 text-lg font-semibold">{result.total_rows}</p>
            </div>
            <div className="card p-4">
              <p className="text-sm text-slate-500">Failed Rows</p>
              <p className="mt-2 text-lg font-semibold text-red-700">{result.failed_rows}</p>
            </div>
            <div className="card p-4">
              <p className="text-sm text-slate-500">Status</p>
              <p
                className={`mt-2 text-lg font-semibold ${
                  result.is_valid ? "text-green-700" : "text-amber-700"
                }`}
              >
                {result.is_valid ? "Valid" : "Invalid"}
              </p>
            </div>
          </div>

          {result.is_valid ? (
            <div className="card p-4">
              <p className="text-sm text-green-700">
                Validation passed. The file is structurally valid for upload.
              </p>
            </div>
          ) : (
            <div className="card overflow-hidden">
              <div className="border-b border-slate-200 p-4">
                <h2 className="text-base font-semibold">Validation Errors</h2>
                <p className="mt-1 text-sm text-slate-600">
                  Each row below failed current import rules and will be rejected until fixed.
                </p>
              </div>

              <div className="divide-y divide-slate-200">
                {result.errors.map((item, index) => (
                  <div key={`${item.row_number}-${index}`} className="p-4">
                    <p className="text-sm font-medium text-slate-900">
                      {item.row_number ? `Row ${item.row_number}` : "File Error"}
                    </p>
                    <p className="mt-1 text-sm text-red-700">{item.error}</p>
                    {item.row_data ? (
                      <pre className="mt-3 overflow-x-auto rounded-md bg-slate-100 p-3 text-xs text-slate-700">
                        {JSON.stringify(item.row_data, null, 2)}
                      </pre>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : null}
    </section>
  );
}

