"use client"

const govtSchemes = [
  { id: 1, title: "MyBharat Volunteering Program", source: "MyBharat", deadline: "Sept 30" },
  { id: 2, title: "PM Internship Scheme", source: "PM Internship", deadline: "Oct 15" },
  { id: 3, title: "National Scholarship Portal - Merit Award", source: "NSP", deadline: "Nov 10" },
]

export default function GovtRadarPage() {
  return (
    <div className="min-h-screen bg-[#FFFBF2] p-6">
      <h1 className="text-2xl font-bold mb-4 text-[#047857]">Govt Radar</h1>
      <p className="text-sm text-gray-500 mb-6">
        Curated opportunities from MyBharat, NSP, and PM Internship Scheme
      </p>

      <div className="flex flex-col gap-4">
        {govtSchemes.map((scheme) => (
          <div
            key={scheme.id}
            className="bg-white border border-[#D1FAE5] rounded-lg shadow-md p-4 max-w-sm"
          >
            <h2 className="text-lg font-bold text-[#047857]">{scheme.title}</h2>
            <p className="text-sm text-gray-500">Source: {scheme.source}</p>
            <p className="text-sm text-gray-500">Deadline: {scheme.deadline}</p>
          </div>
        ))}
      </div>
    </div>
  )
}