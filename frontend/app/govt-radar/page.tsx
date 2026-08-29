"use client";

import { useEffect, useState } from "react";

import { getGovtSchemes, GovtScheme } from "@/lib/api";

function formatSource(source: string) {
  const labels: Record<string, string> = {
    mybharat: "MyBharat",
    nsp: "National Scholarship Portal",
    pminternship: "PM Internship Scheme",
  };

  return labels[source] || source;
}

export default function GovtRadarPage() {
  const [schemes, setSchemes] = useState<GovtScheme[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    getGovtSchemes()
      .then(setSchemes)
      .catch(() =>
        setError(
          "Couldn't load government schemes. Try refreshing."
        )
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">
          Govt Radar
        </h1>

        <p className="text-gray-500 mb-8">
          Curated opportunities from MyBharat, NSP, and PM
          Internship Scheme.
        </p>

        {loading && (
          <p className="text-gray-500">
            Loading schemes...
          </p>
        )}

        {error && (
          <p className="text-red-600">
            {error}
          </p>
        )}

        {!loading && !error && schemes.length === 0 && (
          <p className="text-gray-500">
            No government schemes available right now.
          </p>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {schemes.map((scheme) => (
            <a
              key={scheme.id}
              href={scheme.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow bg-white"
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                  {formatSource(scheme.source)}
                </span>
              </div>

              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {scheme.title}
              </h3>

              <p className="text-sm text-gray-600 mb-3">
                {scheme.organization || "Government of India"}
              </p>

              <div className="text-sm text-gray-500">
                Deadline:{" "}
                <span className="font-medium text-gray-800">
                  {scheme.deadline
                    ? new Date(scheme.deadline).toLocaleDateString(
                        "en-IN",
                        {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                        }
                      )
                    : "TBD"}
                </span>
              </div>
            </a>
          ))}
        </div>
      </div>
    </main>
  );
}