"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { difficultyBadgeClass } from "@/lib/quiz-utils";

export default function QuizPage() {
  const [subjects, setSubjects] = useState([]);
  const [chapters, setChapters] = useState([]);
  const [topics, setTopics] = useState([]);

  const [subjectId, setSubjectId] = useState("");
  const [chapterId, setChapterId] = useState("");
  const [topicId, setTopicId] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [attemptFilter, setAttemptFilter] = useState("all");
  const [retryWrong, setRetryWrong] = useState(false);
  const [questionCountMode, setQuestionCountMode] = useState("all");
  const [questionCountInput, setQuestionCountInput] = useState("10");
  const [availableCount, setAvailableCount] = useState(0);

  const [baseQuestions, setBaseQuestions] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOptionId, setSelectedOptionId] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [markForReview, setMarkForReview] = useState(false);
  const [sessionResults, setSessionResults] = useState([]);
  const [sessionComplete, setSessionComplete] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    api.getSubjects().then(setSubjects).catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!subjectId) {
      setChapters([]);
      setChapterId("");
      return;
    }
    api.getChapters(subjectId).then(setChapters).catch((err) => setError(err.message));
  }, [subjectId]);

  useEffect(() => {
    if (!chapterId) {
      setTopics([]);
      setTopicId("");
      return;
    }
    api.getTopics(chapterId).then(setTopics).catch((err) => setError(err.message));
  }, [chapterId]);

  const currentQuestion = questions[currentIndex];

  function resetSessionState() {
    setFeedback(null);
    setSelectedOptionId(null);
    setCurrentIndex(0);
    setMarkForReview(false);
    setSessionResults([]);
    setSessionComplete(false);
  }

  function getFilterParams() {
    return {
      subject_id: subjectId || undefined,
      chapter_id: chapterId || undefined,
      topic_id: topicId || undefined,
      difficulty: difficulty || undefined,
      unattempted_only: attemptFilter === "unattempted" || undefined,
      attempted_only: attemptFilter === "attempted" || undefined,
      retry_wrong: retryWrong || undefined
    };
  }

  async function checkAvailability(showMessage = false) {
    if (showMessage) {
      setError("");
      setMessage("");
    }
    try {
      const countData = await api.getQuestionsCount(getFilterParams());
      setAvailableCount(countData.total || 0);
      if (showMessage && !countData.total) {
        setMessage("No questions available for current filters.");
      } else if (showMessage) {
        setMessage(`Available questions: ${countData.total}`);
      }
      return countData.total || 0;
    } catch (err) {
      setError(err.message);
      return 0;
    }
  }

  useEffect(() => {
    checkAvailability(false);
  }, [subjectId, chapterId, topicId, difficulty, attemptFilter, retryWrong]);

  useEffect(() => {
    if (questionCountMode !== "specific") {
      return;
    }
    const parsed = Number(questionCountInput);
    if (!Number.isInteger(parsed)) {
      return;
    }
    if (availableCount > 0 && parsed > availableCount) {
      setQuestionCountInput(String(availableCount));
    }
  }, [availableCount, questionCountInput, questionCountMode]);

  async function loadQuestions() {
    setLoading(true);
    setError("");
    setMessage("");
    resetSessionState();
    try {
      const totalAvailable = await checkAvailability(false);
      if (!totalAvailable) {
        setBaseQuestions([]);
        setQuestions([]);
        return;
      }

      let limit = totalAvailable;
      if (questionCountMode === "specific") {
        const parsed = Number(questionCountInput);
        if (!Number.isInteger(parsed) || parsed < 1) {
          setError("Please enter a valid number of questions.");
          return;
        }
        if (parsed > totalAvailable) {
          setError(`Maximum allowed for this filter is ${totalAvailable}.`);
          return;
        }
        limit = parsed;
      }

      const data = await api.getQuestions({
        ...getFilterParams(),
        limit
      });
      setBaseQuestions(data);
      setQuestions(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function submitAnswer() {
    if (!currentQuestion || !selectedOptionId) {
      return;
    }
    setError("");
    try {
      const result = await api.submitAttempt({
        question_id: currentQuestion.id,
        selected_option_id: selectedOptionId,
        marked_for_review: markForReview
      });
      setFeedback(result);
      setSessionResults((prev) => {
        const next = prev.filter((item) => item.questionId !== currentQuestion.id);
        next.push({
          questionId: currentQuestion.id,
          isCorrect: result.is_correct
        });
        return next;
      });
    } catch (err) {
      setError(err.message);
    }
  }

  function moveNext() {
    if (currentIndex >= questions.length - 1) {
      setSessionComplete(true);
      setFeedback(null);
      setSelectedOptionId(null);
      return;
    }
    setFeedback(null);
    setSelectedOptionId(null);
    setMarkForReview(false);
    setCurrentIndex((prev) => prev + 1);
  }

  function retakeSession(wrongOnly) {
    const wrongIds = new Set(sessionResults.filter((item) => !item.isCorrect).map((item) => item.questionId));
    const nextQuestions = wrongOnly ? baseQuestions.filter((q) => wrongIds.has(q.id)) : baseQuestions;
    setQuestions(nextQuestions);
    setSessionComplete(false);
    setSessionResults([]);
    setFeedback(null);
    setSelectedOptionId(null);
    setCurrentIndex(0);
    setMarkForReview(false);
    if (!nextQuestions.length) {
      setMessage("No wrong questions to retake from this session.");
    } else {
      setMessage(
        wrongOnly
          ? `Retake started with ${nextQuestions.length} wrong questions.`
          : `Retake started with ${nextQuestions.length} questions.`
      );
    }
  }

  const totalAnswered = sessionResults.length;
  const correctCount = sessionResults.filter((item) => item.isCorrect).length;
  const wrongCount = totalAnswered - correctCount;
  const coveredSubjects = [...new Set(questions.map((q) => q.subject_name).filter(Boolean))];
  const coveredChapters = [...new Set(questions.map((q) => q.chapter_name).filter(Boolean))];
  const coveredTopics = [...new Set(questions.map((q) => q.topic_name).filter(Boolean))];

  return (
    <section className="space-y-5">
      <h1 className="text-2xl font-semibold">Quiz</h1>

      <div className="card grid gap-3 p-4 md:grid-cols-3 lg:grid-cols-6">
        <select
          className="rounded-md border border-slate-300 px-2 py-2 text-sm"
          value={subjectId}
          onChange={(e) => setSubjectId(e.target.value)}
        >
          <option value="">All Subjects</option>
          {subjects.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </select>

        <select
          className="rounded-md border border-slate-300 px-2 py-2 text-sm"
          value={chapterId}
          onChange={(e) => setChapterId(e.target.value)}
          disabled={!subjectId}
        >
          <option value="">All Chapters</option>
          {chapters.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </select>

        <select
          className="rounded-md border border-slate-300 px-2 py-2 text-sm"
          value={topicId}
          onChange={(e) => setTopicId(e.target.value)}
          disabled={!chapterId}
        >
          <option value="">All Topics</option>
          {topics.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </select>

        <select
          className="rounded-md border border-slate-300 px-2 py-2 text-sm"
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
        >
          <option value="">All Difficulty</option>
          <option value="Easy">Easy</option>
          <option value="Medium">Medium</option>
          <option value="Hard">Hard</option>
        </select>

        <select
          className="rounded-md border border-slate-300 px-2 py-2 text-sm"
          value={attemptFilter}
          onChange={(e) => setAttemptFilter(e.target.value)}
        >
          <option value="all">All Questions</option>
          <option value="attempted">Attempted</option>
          <option value="unattempted">Unattempted</option>
        </select>

        <button
          className="rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
          onClick={loadQuestions}
        >
          {loading ? "Loading..." : "Start Quiz"}
        </button>
      </div>

      <div className="card flex flex-wrap items-end gap-4 p-4">
        <label className="inline-flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={retryWrong}
            onChange={(e) => setRetryWrong(e.target.checked)}
          />
          Retry Wrong Questions
        </label>

        <div className="space-y-1">
          <p className="text-xs text-slate-500">Number of Questions</p>
          <select
            className="rounded-md border border-slate-300 px-2 py-2 text-sm"
            value={questionCountMode}
            onChange={(e) => setQuestionCountMode(e.target.value)}
          >
            <option value="all">All Available</option>
            <option value="specific">Specific Number</option>
          </select>
        </div>

        <div className="space-y-1">
          <p className="text-xs text-slate-500">Specific Count</p>
          <input
            type="number"
            min={1}
            max={availableCount || 1}
            disabled={questionCountMode !== "specific"}
            className="w-32 rounded-md border border-slate-300 px-2 py-2 text-sm disabled:bg-slate-100"
            value={questionCountInput}
            onChange={(e) => setQuestionCountInput(e.target.value)}
          />
          <p className="text-xs text-slate-500">Max for current filter: {availableCount}</p>
        </div>

        <p className="text-sm text-slate-600">Available: {availableCount}</p>
      </div>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {message ? <p className="text-sm text-blue-700">{message}</p> : null}

      {!loading && questions.length === 0 ? (
        <p className="text-sm text-slate-600">Load questions with filters to begin.</p>
      ) : null}

      {currentQuestion ? (
        <article className="card p-5">
          <div className="mb-4 flex items-center justify-between">
            <p className="text-sm text-slate-500">
              Question {currentIndex + 1} / {questions.length}
            </p>
            <span
              className={`rounded-full px-2 py-1 text-xs font-semibold ${difficultyBadgeClass(
                currentQuestion.difficulty
              )}`}
            >
              {currentQuestion.difficulty}
            </span>
          </div>

          <h2 className="mb-4 text-lg font-semibold">{currentQuestion.question_text}</h2>

          <div className="space-y-2">
            {currentQuestion.options.map((option) => (
              <label
                key={option.id}
                className={`block cursor-pointer rounded-md border p-3 text-sm ${
                  selectedOptionId === option.id
                    ? "border-blue-500 bg-blue-50"
                    : "border-slate-200 bg-white"
                }`}
              >
                <input
                  className="mr-2"
                  type="radio"
                  name={`question-${currentQuestion.id}`}
                  checked={selectedOptionId === option.id}
                  onChange={() => setSelectedOptionId(option.id)}
                />
                {option.option_text}
              </label>
            ))}
          </div>

          <label className="mt-4 inline-flex items-center gap-2 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={markForReview}
              onChange={(e) => setMarkForReview(e.target.checked)}
            />
            Mark this attempt for review
          </label>

          {!feedback ? (
            <button
              className="mt-4 rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
              onClick={submitAnswer}
            >
              Submit Answer
            </button>
          ) : (
            <div className="mt-4 space-y-3 rounded-md border border-slate-200 bg-slate-50 p-3">
              <p
                className={`text-sm font-medium ${
                  feedback.is_correct ? "text-green-700" : "text-red-700"
                }`}
              >
                {feedback.is_correct ? "Correct answer." : "Incorrect answer."}
              </p>
              <p className="text-sm text-slate-700">{feedback.explanation}</p>
              <button
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                onClick={moveNext}
              >
                {currentIndex >= questions.length - 1 ? "Finish Quiz" : "Next Question"}
              </button>
            </div>
          )}
        </article>
      ) : null}

      {sessionComplete ? (
        <article className="card space-y-4 p-5">
          <h2 className="text-xl font-semibold">Quiz Summary</h2>
          <div className="grid gap-3 md:grid-cols-3">
            <div className="rounded-md bg-slate-100 p-3 text-sm">
              <p className="text-slate-500">Total Questions</p>
              <p className="text-lg font-semibold">{questions.length}</p>
            </div>
            <div className="rounded-md bg-green-50 p-3 text-sm">
              <p className="text-green-700">Correct</p>
              <p className="text-lg font-semibold text-green-700">{correctCount}</p>
            </div>
            <div className="rounded-md bg-red-50 p-3 text-sm">
              <p className="text-red-700">Wrong</p>
              <p className="text-lg font-semibold text-red-700">{wrongCount}</p>
            </div>
          </div>

          <div className="space-y-2 text-sm text-slate-700">
            <p>
              <span className="font-medium">Subjects covered:</span>{" "}
              {coveredSubjects.length ? coveredSubjects.join(", ") : "N/A"}
            </p>
            <p>
              <span className="font-medium">Chapters covered:</span>{" "}
              {coveredChapters.length ? coveredChapters.join(", ") : "N/A"}
            </p>
            <p>
              <span className="font-medium">Topics covered:</span>{" "}
              {coveredTopics.length ? coveredTopics.join(", ") : "N/A"}
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
              onClick={() => retakeSession(false)}
            >
              Retake Quiz (All)
            </button>
            <button
              className="rounded-md bg-amber-600 px-4 py-2 text-sm font-medium text-white hover:bg-amber-700"
              onClick={() => retakeSession(true)}
            >
              Retake Quiz (Wrong Only)
            </button>
          </div>
        </article>
      ) : null}
    </section>
  );
}
