"use client"

import { useState } from "react"

const opportunities = [
  { id: 1, title: "AI Buildathon 2026", category: "Hackathon", deadline: "Sept 26" },
  { id: 2, title: "Google STEP Internship", category: "Internship", deadline: "Oct 5" },
  { id: 3, title: "Inspire Scholarship", category: "Scholarship", deadline: "Nov 1" },
  { id: 4, title: "MyBharat Fellowship", category: "Fellowship", deadline: "Oct 20" },
]

const categories = ["All", "Hackathon", "Internship", "Scholarship", "Fellowship"]

export default function TrackerPage() {
  const [selectedCategory, setSelectedCategory] = useState("All")

  const filteredOpportunities =
    selectedCategory === "All"
      ? opportunities
      : opportunities.filter((o) => o.category === selectedCategory)

  return (
    <div className="min-h-screen bg-[#FFFBF2]">
      <div className="max-w-5xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-4 text-[#047857]">My Tracker</h1>

        <div className="flex gap-2 mb-6 flex-wrap">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition ${
                selectedCategory === cat
                  ? "bg-[#047857] text-white"
                  : "bg-[#D1FAE5] text-[#047857]"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredOpportunities.map((opp) => (
            <div
              key={opp.id}
              className="bg-white border border-[#D1FAE5] rounded-lg shadow-sm hover:shadow-md transition p-4"
            >
              <h2 className="text-lg font-bold text-[#047857]">{opp.title}</h2>
              <p className="text-sm text-gray-500">Category: {opp.category}</p>
              <p className="text-sm text-gray-500">Deadline: {opp.deadline}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}