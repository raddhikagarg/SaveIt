"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        <Link href="/" className="text-lg font-bold text-gray-900">
          SaveIt
        </Link>
        <div className="flex items-center gap-6 text-sm font-medium">
          <Link href="/" className="text-gray-600 hover:text-gray-900">
            Dashboard
          </Link>
          <Link href="/tracker" className="text-gray-600 hover:text-gray-900">
            My Tracker
          </Link>
          <Link href="/govt-radar" className="text-gray-600 hover:text-gray-900">
            Govt Radar
          </Link>
          {user && (
            <button
              onClick={logout}
              className="text-gray-500 hover:text-red-600 transition-colors"
            >
              Log out
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
