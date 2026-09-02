"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";

export default function LinkTelegram() {
  const { token } = useAuth();
  const [linkData, setLinkData] = useState<{ code: string; instructions: string; expires_at: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const generateCode = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/link/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ platform: "telegram" }),
      });
      if (!res.ok) throw new Error("Failed to generate code");
      const data = await res.json();
      setLinkData(data);
    } catch {
      setError("Couldn't generate a link code. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="border border-gray-200 rounded-xl p-4 bg-white">
      <h3 className="font-semibold text-gray-900 mb-1">Connect Telegram</h3>
      <p className="text-sm text-gray-500 mb-3">
        Link your Telegram so reels and messages you send the bot show up here.
      </p>

      {!linkData && (
        <button
          onClick={generateCode}
          disabled={loading}
          className="bg-gray-900 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50"
        >
          {loading ? "Generating..." : "Get link code"}
        </button>
      )}

      {error && <p className="text-red-600 text-sm mt-2">{error}</p>}

      {linkData && (
        <div className="mt-2 bg-gray-50 border border-gray-200 rounded-lg p-3">
          <p className="text-sm text-gray-800 font-medium mb-1">
            Code: <span className="font-mono">{linkData.code}</span>
          </p>
          <p className="text-sm text-gray-600">{linkData.instructions}</p>
          <p className="text-xs text-gray-400 mt-1">
            Expires at {new Date(linkData.expires_at).toLocaleTimeString()}
          </p>
        </div>
      )}
    </div>
  );
}
