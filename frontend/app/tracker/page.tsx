"use client";

import { useEffect, useState } from "react";

import { useAuth } from "@/lib/auth-context";
import { getOpportunities, Opportunity } from "@/lib/api";

import OpportunityCard from "../components/OpportunityCard";
import AuthForm from "./components/AuthForm";

const categories = [
  "All",
  "hackathon",
  "internship",
  "scholarship",
  "fellowship",
  "course",
  "meetup",
  "government_scheme",
  "other",
];

function formatCategory(category: string) {
  if (category === "All") return "All";

  return category
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function TrackerPage() {
  const { user, token, loading: authLoading } = useAuth();

  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState("All");

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
        setError("Couldn't load your tracker. Try refreshing.")
      )
      .finally(() => setLoading(false));
  }, [user, token]);

  const filteredOpportunities =
    selectedCategory === "All"
      ? opportunities
      : opportunities.filter(
          (opportunity) => opportunity.category === selectedCategory
        );

  if (authLoading) {
    return <main className="min-h-screen bg-gray-50" />;
  }

  if (!user) {
    return (
      <main className="min-h-screen bg-gray-50 px-6 py-10 flex flex-col items-center justify-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900">
          My Tracker
        </h1>

        <p className="text-gray-500 mb-2">
          Sign in to see your tracked opportunities.
        </p>

        
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">
          My Tracker
        </h1>

        <p className="text-gray-500 mb-6">
          Everything you've saved, filtered and sorted by deadline.
        </p>

        <div className="flex gap-2 mb-8 flex-wrap">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                selectedCategory === cat
                  ? "bg-gray-900 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {formatCategory(cat)}
            </button>
          ))}
        </div>

        {loading && (
          <p className="text-gray-500">
            Loading your tracker...
          </p>
        )}

        {error && (
          <p className="text-red-600">
            {error}
          </p>
        )}

        {!loading && !error && filteredOpportunities.length === 0 && (
          <p className="text-gray-500">
            {opportunities.length === 0
              ? "No opportunities tracked yet. Share a reel or link to get started!"
              : "No opportunities match this category."}
          </p>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredOpportunities.map((opportunity) => (
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