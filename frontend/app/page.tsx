"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import OpportunityCard from "./components/OpportunityCard";
import { useAuth } from "@/lib/auth-context";
import { getOpportunities, Opportunity } from "@/lib/api";

export default function Dashboard() {
  const { user, token, loading: authLoading } = useAuth();
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    getOpportunities(user.id, token)
      .then(setOpportunities)
      .catch(() => setError("Couldn't load your opportunities. Try refreshing."))
      .finally(() => setLoading(false));
  }, [user, token]);

  if (authLoading) {
    return <main className="min-h-screen bg-gray-50" />;
  }

  if (!user) {
    return (
      <main className="min-h-screen bg-gray-50 px-6 py-10 flex flex-col items-center justify-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900">Welcome to SaveIt</h1>
        <p className="text-gray-500 mb-2">Log in to see your tracked opportunities.</p>
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
        <h1 className="text-2xl font-bold text-gray-900 mb-1">SaveIt</h1>
        <p className="text-gray-500 mb-8">
          Your tracked opportunities, deadlines, and government schemes.
        </p>

        {loading && <p className="text-gray-500">Loading your opportunities...</p>}
        {error && <p className="text-red-600">{error}</p>}

        {!loading && !error && opportunities.length === 0 && (
          <p className="text-gray-500">
            No opportunities tracked yet. Share a reel or link to get started!
          </p>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {opportunities.map((opportunity) => (
            <OpportunityCard key={opportunity.id} opportunity={opportunity} />
          ))}
        </div>
      </div>
    </main>
  );
}
