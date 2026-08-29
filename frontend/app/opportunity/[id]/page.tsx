"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

import { useAuth } from "@/lib/auth-context";
import {
  getOpportunity,
  confirmOpportunity,
  Opportunity,
} from "@/lib/api";

function formatCategory(category: string) {
  return category
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function OpportunityDetail() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();

  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    if (!id) return;

    setLoading(true);
    setError(null);

    getOpportunity(id, token)
      .then(setOpportunity)
      .catch(() => setError("Couldn't load this opportunity."))
      .finally(() => setLoading(false));
  }, [id, token]);

  const handleConfirm = async () => {
    if (!opportunity) return;

    setConfirming(true);
    setError(null);

    try {
      const updated = await confirmOpportunity(opportunity.id, token);
      setOpportunity(updated);
    } catch {
      setError("Couldn't confirm this deadline. Try again.");
    } finally {
      setConfirming(false);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 px-6 py-10">
        <div className="max-w-2xl mx-auto">
          <p className="text-gray-500">Loading opportunity...</p>
        </div>
      </main>
    );
  }

  if (error || !opportunity) {
    return (
      <main className="min-h-screen bg-gray-50 px-6 py-10">
        <div className="max-w-2xl mx-auto">
          <Link
            href="/"
            className="text-sm text-gray-500 hover:text-gray-800"
          >
            Back to dashboard
          </Link>

          <p className="text-red-600 mt-4">
            {error || "Opportunity not found."}
          </p>
        </div>
      </main>
    );
  }

  const confidenceColor =
    opportunity.confidence_score >= 0.8
      ? "bg-green-100 text-green-700"
      : opportunity.confidence_score >= 0.5
        ? "bg-yellow-100 text-yellow-700"
        : "bg-red-100 text-red-700";

  const deadlineDisplay = opportunity.deadline
    ? new Date(opportunity.deadline).toLocaleDateString("en-IN", {
        year: "numeric",
        month: "short",
        day: "numeric",
      })
    : "TBD";

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="max-w-2xl mx-auto">
        <Link
          href="/"
          className="text-sm text-gray-500 hover:text-gray-800 mb-6 inline-block"
        >
          Back to dashboard
        </Link>

        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              {formatCategory(opportunity.category)}
            </span>

            <span
              className={`text-xs font-medium px-2 py-1 rounded-full ${confidenceColor}`}
            >
              {Math.round(opportunity.confidence_score * 100)}% confidence
            </span>
          </div>

          <h1 className="text-2xl font-bold text-gray-900 mb-1">
            {opportunity.title}
          </h1>

          <p className="text-gray-600 mb-6">
            {opportunity.organization || "Unknown organization"}
          </p>

          {opportunity.status === "needs_confirmation" && (
            <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm text-yellow-800 mb-3">
                This deadline was extracted with low confidence. Please
                confirm it's correct.
              </p>

              <button
                onClick={handleConfirm}
                disabled={confirming}
                className="bg-yellow-600 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-yellow-700 transition-colors disabled:opacity-50"
              >
                {confirming
                  ? "Confirming..."
                  : "Confirm this deadline"}
              </button>
            </div>
          )}

          <div className="space-y-3 text-sm">
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span className="text-gray-500">Deadline</span>

              <span className="font-medium text-gray-900">
                {deadlineDisplay}
              </span>
            </div>

            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span className="text-gray-500">Eligibility</span>

              <span className="font-medium text-gray-900 text-right">
                {opportunity.eligibility || "Not specified"}
              </span>
            </div>

            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span className="text-gray-500">Stipend / Reward</span>

              <span className="font-medium text-gray-900">
                {opportunity.stipend || "Not specified"}
              </span>
            </div>
          </div>

          {opportunity.raw_source_url && (
            <div className="mt-6">
              <a
                href={opportunity.raw_source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block bg-gray-900 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors"
              >
                View source
              </a>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}