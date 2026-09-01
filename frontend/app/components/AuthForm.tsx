"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";

export default function AuthForm() {
    const { login } = useAuth();
    const [mode, setMode] = useState<"login" | "register">("login");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [name, setName] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setSubmitting(true);

        const endpoint = mode === "login" ? "/auth/login" : "/auth/register";
        const body =
            mode === "login" ? { email, password } : { email, password, name };

        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || "Something went wrong");
            }
            login(data.access_token, data.user);
        } catch (err: any) {
            setError(err.message || "Something went wrong");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="w-full max-w-sm flex flex-col gap-3">
            {mode === "register" && (
                <input
                    type="text"
                    placeholder="Name (optional)"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                />
            )}
            <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
            />
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
            />

            {error && <p className="text-red-600 text-sm">{error}</p>}

            <button
                type="submit"
                disabled={submitting}
                className="bg-gray-900 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50"
            >
                {submitting ? "Please wait..." : mode === "login" ? "Log in" : "Sign up"}
            </button>

            <button
                type="button"
                onClick={() => {
                    setMode(mode === "login" ? "register" : "login");
                    setError(null);
                }}
                className="text-sm text-gray-500 hover:text-gray-800"
            >
                {mode === "login" ? "Need an account? Sign up" : "Already have an account? Log in"}
            </button>
        </form>
    );
}