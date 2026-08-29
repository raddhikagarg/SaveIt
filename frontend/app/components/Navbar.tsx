import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        <Link href="/" className="text-lg font-bold text-gray-900">
          SaveIt
        </Link>

        <div className="flex gap-6 text-sm font-medium">
          <Link href="/" className="text-gray-600 hover:text-gray-900">
            Dashboard
          </Link>
          <Link href="/tracker" className="text-gray-600 hover:text-gray-900">
            My Tracker
          </Link>
          <Link href="/govt-radar" className="text-gray-600 hover:text-gray-900">
            Govt Radar
          </Link>
        </div>
      </div>
    </nav>
  );
}