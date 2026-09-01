"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { loginUser } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const data = await loginUser(email, password);
      login(data.access_token, data.user);
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50 px-6">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-xl border border-gray-200 shadow-sm w-full max-w-sm">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Log in to SaveIt</h1>
        {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full border border-gray-200 rounded-lg px-3 py-2 mb-3 text-sm"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="w-full border border-gray-200 rounded-lg px-3 py-2 mb-4 text-sm"
        />
        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-gray-900 text-white rounded-lg py-2 text-sm font-medium disabled:opacity-50"
        >
          {submitting ? "Logging in..." : "Log in"}
        </button>
        <p className="text-sm mt-4 text-center text-gray-500">
          No account?{" "}
          <Link href="/register" className="text-gray-900 font-medium">
            Register
          </Link>
        </p>
      </form>
    </main>
  );
}
