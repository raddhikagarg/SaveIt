"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import OpportunityCard from "./components/OpportunityCard";

import { useAuth } from "@/lib/auth-context";
import {
  getOpportunities,
  submitRawContent,
  Opportunity,
} from "@/lib/api";

export default function Dashboard() {
  const { user, token, loading: authLoading } = useAuth();

  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showAdd, setShowAdd] = useState(false);
  const [url, setUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    getOpportunities(user.id, token)
      .then(setOpportunities)
      .catch(() =>
        setError("Couldn't load your opportunities. Try refreshing.")
      )
      .finally(() => setLoading(false));
  }, [user, token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!user) return;

    const trimmedUrl = url.trim();

    if (!trimmedUrl) {
      setSubmitError("Please paste a link first.");
      return;
    }

    try {
      new URL(trimmedUrl);
    } catch {
      setSubmitError("Please enter a valid URL.");
      return;
    }

    setSubmitting(true);
    setSubmitError(null);

    try {
      const opportunity = await submitRawContent(
        user.id,
        trimmedUrl,
        token
      );

      setOpportunities((current) => [opportunity, ...current]);

      setUrl("");
      setShowAdd(false);
    } catch (err) {
      setSubmitError(
        err instanceof Error
          ? err.message
          : "Couldn't save this link. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (authLoading) {
    return <main className="min-h-screen bg-gray-50" />;
  }

  if (!user) {
    return (
      <main className="min-h-screen bg-gray-50 px-6 py-10 flex flex-col items-center justify-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome to SaveIt
        </h1>

        <p className="text-gray-500 mb-2">
          Log in to see your tracked opportunities.
        </p>

        <Link
          href="/login"
          className="bg-gray-900 text-white rounded-lg px-6 py-2 text-sm font-medium"
        >
          Log in
        </Link>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <div className="flex items-start justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-1">
              SaveIt
            </h1>

            <p className="text-gray-500">
              Your tracked opportunities, deadlines, and government schemes.
            </p>
          </div>

          {/* Add button */}
          <button
            onClick={() => {
              setShowAdd((current) => !current);
              setSubmitError(null);
            }}
            className="shrink-0 inline-flex items-center gap-2 bg-gray-900 text-white rounded-lg px-4 py-2.5 text-sm font-medium hover:bg-gray-800 transition"
          >
            <span className="text-lg leading-none">+</span>
            Add Reel / Link
          </button>
        </div>

        {/* Add link form */}
        {showAdd && (
          <form
            onSubmit={handleSubmit}
            className="mb-8 rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
          >
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Paste an Instagram Reel or opportunity link..."
                autoFocus
                disabled={submitting}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-900 outline-none focus:border-gray-500 focus:ring-1 focus:ring-gray-300 disabled:bg-gray-100"
              />

              <button
                type="submit"
                disabled={submitting}
                className="rounded-lg bg-gray-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {submitting ? "Saving..." : "Save"}
              </button>

              <button
                type="button"
                onClick={() => {
                  setShowAdd(false);
                  setUrl("");
                  setSubmitError(null);
                }}
                disabled={submitting}
                className="rounded-lg px-4 py-2.5 text-sm font-medium text-gray-500 hover:bg-gray-100 transition"
              >
                Cancel
              </button>
            </div>

            {submitError && (
              <p className="mt-3 text-sm text-red-600">
                {submitError}
              </p>
            )}

            {!submitError && (
              <p className="mt-3 text-xs text-gray-400">
                SaveIt will extract the opportunity details automatically.
              </p>
            )}
          </form>
        )}

        {/* Loading */}
        {loading && (
          <p className="text-gray-500">
            Loading your opportunities...
          </p>
        )}

        {/* General error */}
        {error && (
          <p className="text-red-600">
            {error}
          </p>
        )}

        {/* Empty state */}
        {!loading && !error && opportunities.length === 0 && (
          <div className="rounded-xl border border-dashed border-gray-300 bg-white px-6 py-12 text-center">
            <p className="text-gray-600 mb-4">
              No opportunities tracked yet.
            </p>

            <p className="text-sm text-gray-400 mb-5">
              Paste an Instagram Reel or opportunity link and SaveIt will
              extract the details for you.
            </p>

            <button
              onClick={() => {
                setShowAdd(true);
                setSubmitError(null);
              }}
              className="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-gray-800 transition"
            >
              <span className="text-lg leading-none">+</span>
              Add your first opportunity
            </button>
          </div>
        )}

        {/* Opportunity cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {opportunities.map((opportunity) => (
            <OpportunityCard
              key={opportunity.id}
              opportunity={opportunity}
            />
          ))}
        </div>

      </div>
    </main>
  );
}