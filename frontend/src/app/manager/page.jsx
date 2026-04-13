"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { difficultyBadgeClass } from "@/lib/quiz-utils";

const EMPTY_EDIT = {
  topic_id: "",
  question_text: "",
  difficulty: "Easy",
  explanation: "",
  options: [
    { option_text: "", is_correct: true },
    { option_text: "", is_correct: false },
    { option_text: "", is_correct: false },
    { option_text: "", is_correct: false }
  ]
};

export default function ManagerPage() {
  const [subjects, setSubjects] = useState([]);
  const [chapters, setChapters] = useState([]);
  const [topics, setTopics] = useState([]);
  const [filterSubjectId, setFilterSubjectId] = useState("");
  const [filterChapterId, setFilterChapterId] = useState("");
  const [filterTopicId, setFilterTopicId] = useState("");
  const [filterDifficulty, setFilterDifficulty] = useState("");

  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [editingQuestionId, setEditingQuestionId] = useState(null);
  const [editForm, setEditForm] = useState(EMPTY_EDIT);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.getSubjects().then(setSubjects).catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!filterSubjectId) {
      setChapters([]);
      setFilterChapterId("");
      setTopics([]);
      setFilterTopicId("");
      return;
    }
    api
      .getChapters(filterSubjectId)
      .then((data) => {
        setChapters(data);
        setFilterChapterId("");
        setTopics([]);
        setFilterTopicId("");
      })
      .catch((err) => setError(err.message));
  }, [filterSubjectId]);

  useEffect(() => {
    if (!filterChapterId) {
      setTopics([]);
      setFilterTopicId("");
      return;
    }
    api
      .getTopics(filterChapterId)
      .then((data) => {
        setTopics(data);
        setFilterTopicId("");
      })
      .catch((err) => setError(err.message));
  }, [filterChapterId]);

  async function loadQuestions() {
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const data = await api.getQuestions({
        subject_id: filterSubjectId || undefined,
        chapter_id: filterChapterId || undefined,
        topic_id: filterTopicId || undefined,
        difficulty: filterDifficulty || undefined,
        randomize: false,
        limit: 100
      });
      setQuestions(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function startEdit(question) {
    setEditingQuestionId(question.id);
    setEditForm({
      topic_id: String(question.topic_id),
      question_text: question.question_text,
      difficulty: question.difficulty,
      explanation: question.explanation,
      options: question.options.map((option) => ({
        option_text: option.option_text,
        is_correct: option.is_correct
      }))
    });
    setError("");
    setMessage("");
  }

  function updateOptionText(index, value) {
    setEditForm((prev) => ({
      ...prev,
      options: prev.options.map((item, i) =>
        i === index ? { ...item, option_text: value } : item
      )
    }));
  }

  function setCorrectOption(index) {
    setEditForm((prev) => ({
      ...prev,
      options: prev.options.map((item, i) => ({ ...item, is_correct: i === index }))
    }));
  }

  async function saveEdit() {
    if (!editingQuestionId) {
      return;
    }
    const correctCount = editForm.options.filter((option) => option.is_correct).length;
    if (correctCount !== 1) {
      setError("Exactly one option must be correct.");
      return;
    }
    if (editForm.options.some((option) => !option.option_text.trim())) {
      setError("All options must be non-empty.");
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");
    try {
      await api.updateQuestion(editingQuestionId, {
        topic_id: Number(editForm.topic_id),
        question_text: editForm.question_text,
        difficulty: editForm.difficulty,
        explanation: editForm.explanation,
        options: editForm.options
      });
      setMessage("Question updated.");
      setEditingQuestionId(null);
      setEditForm(EMPTY_EDIT);
      await loadQuestions();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function deleteQuestion(questionId) {
    const confirmed = window.confirm("Delete this question permanently?");
    if (!confirmed) {
      return;
    }
    setError("");
    setMessage("");
    try {
      await api.deleteQuestion(questionId);
      setMessage("Question deleted.");
      setQuestions((prev) => prev.filter((item) => item.id !== questionId));
      if (editingQuestionId === questionId) {
        setEditingQuestionId(null);
        setEditForm(EMPTY_EDIT);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="space-y-5">
      <h1 className="text-2xl font-semibold">Question Manager</h1>

      <div className="card grid gap-3 p-4 md:grid-cols-2 lg:grid-cols-5">
        <select
          className="rounded-md border border-slate-300 px-2 py-2 text-sm"
          value={filterSubjectId}
          onChange={(e) => setFilterSubjectId(e.target.value)}
        >
          <option value="">All Subjects</option>
          {subjects.map((subject) => (
            <option key={subject.id} value={subject.id}>
              {subject.name}
            </option>
          ))}
        </select>

        <select
          className="rounded-md border border-slate-300 px-2 py-2 text-sm"
          value={filterChapterId}
          onChange={(e) => setFilterChapterId(e.target.value)}
          disabled={!filterSubjectId}
        >
          <option value="">All Chapters</option>
          {chapters.map((chapter) => (
            <option key={chapter.id} value={chapter.id}>
              {chapter.name}
            </option>
          ))}
        </select>

        <select
          className="rounded-md border border-slate-300 px-2 py-2 text-sm"
          value={filterTopicId}
          onChange={(e) => setFilterTopicId(e.target.value)}
          disabled={!filterChapterId}
        >
          <option value="">All Topics</option>
          {topics.map((topic) => (
            <option key={topic.id} value={topic.id}>
              {topic.name}
            </option>
          ))}
        </select>

        <select
          className="rounded-md border border-slate-300 px-2 py-2 text-sm"
          value={filterDifficulty}
          onChange={(e) => setFilterDifficulty(e.target.value)}
        >
          <option value="">All Difficulty</option>
          <option value="Easy">Easy</option>
          <option value="Medium">Medium</option>
          <option value="Hard">Hard</option>
        </select>

        <button
          className="rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
          onClick={loadQuestions}
        >
          {loading ? "Loading..." : "Load Questions"}
        </button>
      </div>

      {message ? <p className="text-sm text-green-700">{message}</p> : null}
      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <div className="space-y-3">
        {questions.map((question) => (
          <article key={question.id} className="card p-4">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm text-slate-500">
                ID: {question.id} | Topic ID: {question.topic_id}
              </p>
              <span
                className={`rounded-full px-2 py-1 text-xs font-semibold ${difficultyBadgeClass(
                  question.difficulty
                )}`}
              >
                {question.difficulty}
              </span>
            </div>

            {editingQuestionId === question.id ? (
              <div className="space-y-3">
                <select
                  className="w-full rounded-md border border-slate-300 px-2 py-2 text-sm"
                  value={editForm.topic_id}
                  onChange={(e) =>
                    setEditForm((prev) => ({ ...prev, topic_id: e.target.value }))
                  }
                >
                  <option value="">Select topic</option>
                  {topics.map((topic) => (
                    <option key={topic.id} value={topic.id}>
                      {topic.name}
                    </option>
                  ))}
                </select>

                <textarea
                  className="w-full rounded-md border border-slate-300 p-2 text-sm"
                  value={editForm.question_text}
                  onChange={(e) =>
                    setEditForm((prev) => ({ ...prev, question_text: e.target.value }))
                  }
                  rows={3}
                />

                <select
                  className="w-full rounded-md border border-slate-300 px-2 py-2 text-sm"
                  value={editForm.difficulty}
                  onChange={(e) =>
                    setEditForm((prev) => ({ ...prev, difficulty: e.target.value }))
                  }
                >
                  <option value="Easy">Easy</option>
                  <option value="Medium">Medium</option>
                  <option value="Hard">Hard</option>
                </select>

                <textarea
                  className="w-full rounded-md border border-slate-300 p-2 text-sm"
                  value={editForm.explanation}
                  onChange={(e) =>
                    setEditForm((prev) => ({ ...prev, explanation: e.target.value }))
                  }
                  rows={2}
                />

                <div className="space-y-2">
                  {editForm.options.map((option, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <input
                        type="radio"
                        name={`correct-option-${question.id}`}
                        checked={option.is_correct}
                        onChange={() => setCorrectOption(index)}
                      />
                      <input
                        type="text"
                        className="w-full rounded-md border border-slate-300 p-2 text-sm"
                        value={option.option_text}
                        onChange={(e) => updateOptionText(index, e.target.value)}
                      />
                    </div>
                  ))}
                </div>

                <div className="flex gap-2">
                  <button
                    className="rounded-md bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700"
                    onClick={saveEdit}
                    disabled={saving}
                  >
                    {saving ? "Saving..." : "Save"}
                  </button>
                  <button
                    className="rounded-md bg-slate-500 px-3 py-2 text-sm font-medium text-white hover:bg-slate-600"
                    onClick={() => {
                      setEditingQuestionId(null);
                      setEditForm(EMPTY_EDIT);
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <h2 className="text-base font-semibold">{question.question_text}</h2>
                <ul className="list-disc space-y-1 pl-6 text-sm text-slate-700">
                  {question.options.map((option) => (
                    <li key={option.id}>
                      {option.option_text}
                      {option.is_correct ? " (Correct)" : ""}
                    </li>
                  ))}
                </ul>
                <p className="text-sm text-slate-600">{question.explanation}</p>
                <div className="flex gap-2">
                  <button
                    className="rounded-md bg-amber-600 px-3 py-2 text-sm font-medium text-white hover:bg-amber-700"
                    onClick={() => startEdit(question)}
                  >
                    Edit
                  </button>
                  <button
                    className="rounded-md bg-red-600 px-3 py-2 text-sm font-medium text-white hover:bg-red-700"
                    onClick={() => deleteQuestion(question.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            )}
          </article>
        ))}
      </div>

      {!loading && !questions.length ? (
        <p className="text-sm text-slate-600">No questions loaded yet.</p>
      ) : null}
    </section>
  );
}

