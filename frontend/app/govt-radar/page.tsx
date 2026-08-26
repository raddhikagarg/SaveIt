"use client"

import Link from "next/link"

const govtSchemes = [
  { id: 1, title: "MyBharat Volunteering Program", source: "MyBharat", deadline: "Sept 30" },
  { id: 2, title: "PM Internship Scheme", source: "PM Internship", deadline: "Oct 15" },
  { id: 3, title: "National Scholarship Portal - Merit Award", source: "NSP", deadline: "Nov 10" },
]

function NavBar() {
  return (
    <div className="flex gap-6 mb-8 border-b border-[#D1FAE5] pb-4">
      <Link href="/tracker" className="text-gray-500 hover:text-[#047857]">My Tracker</Link>
      <Link href="/govt-radar" className="text-[#047857] font-semibold">Govt Radar</Link>
    </div>
  )
}

export default function GovtRadarPage() {
  return (
    <div className="min-h-screen bg-[#FFFBF2]">
      <div className="max-w-5xl mx-auto px-6 py-8">
        <NavBar />
        <h1 className="text-2xl font-bold mb-2 text-[#047857]">Govt Radar</h1>
        <p className="text-sm text-gray-500 mb-6">
          Curated opportunities from MyBharat, NSP, and PM Internship Scheme
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {govtSchemes.map((scheme) => (
            <div
              key={scheme.id}
              className="bg-white border border-[#D1FAE5] rounded-lg shadow-sm hover:shadow-md transition p-4"
            >
              <h2 className="text-lg font-bold text-[#047857]">{scheme.title}</h2>
              <p className="text-sm text-gray-500">Source: {scheme.source}</p>
              <p className="text-sm text-gray-500">Deadline: {scheme.deadline}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}