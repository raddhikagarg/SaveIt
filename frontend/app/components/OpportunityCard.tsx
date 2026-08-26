import Link from "next/link";
import { Opportunity } from "@/lib/mockData";

export default function OpportunityCard({ opportunity }: { opportunity: Opportunity }) {
  const confidenceColor =
    opportunity.confidenceScore >= 0.8
      ? "bg-green-100 text-green-700"
      : opportunity.confidenceScore >= 0.5
      ? "bg-yellow-100 text-yellow-700"
      : "bg-red-100 text-red-700";

  return (
    <Link
      href={`/opportunity/${opportunity.id}`}
      className="block border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow bg-white"
    >
      <div className="flex justify-between items-start mb-2">
        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
          {opportunity.category}
        </span>
        <span className={`text-xs font-medium px-2 py-1 rounded-full ${confidenceColor}`}>
          {Math.round(opportunity.confidenceScore * 100)}% match
        </span>
      </div>

      <h3 className="text-lg font-semibold text-gray-900 mb-1">
        {opportunity.title}
      </h3>
      <p className="text-sm text-gray-600 mb-3">{opportunity.organization}</p>

      <div className="flex justify-between items-center text-sm">
        <span className="text-gray-500">
          Deadline: <span className="font-medium text-gray-800">{opportunity.deadline}</span>
        </span>
        {opportunity.stipend && (
          <span className="text-gray-700 font-medium">{opportunity.stipend}</span>
        )}
      </div>
    </Link>
  );
}