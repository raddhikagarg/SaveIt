import { mockOpportunities } from "@/lib/mockData";
import Link from "next/link";
import { notFound } from "next/navigation";

export default async function OpportunityDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  const opportunity = mockOpportunities.find((o) => o.id === id);

  if (!opportunity) {
    notFound();
  }

  const confidenceColor =
    opportunity.confidenceScore >= 0.8
      ? "bg-green-100 text-green-700"
      : opportunity.confidenceScore >= 0.5
      ? "bg-yellow-100 text-yellow-700"
      : "bg-red-100 text-red-700";

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="max-w-2xl mx-auto">
        <Link
          href="/"
          className="text-sm text-gray-500 hover:text-gray-800 mb-6 inline-block"
        >
          Back to dashboard
        </Link>

        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              {opportunity.category}
            </span>

            <span
              className={`text-xs font-medium px-2 py-1 rounded-full ${confidenceColor}`}
            >
              {Math.round(opportunity.confidenceScore * 100)}% confidence
            </span>
          </div>

          <h1 className="text-2xl font-bold text-gray-900 mb-1">
            {opportunity.title}
          </h1>

          <p className="text-gray-600 mb-6">{opportunity.organization}</p>

          <div className="space-y-3 text-sm">
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span className="text-gray-500">Deadline</span>
              <span className="font-medium text-gray-900">
                {opportunity.deadline}
              </span>
            </div>

            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span className="text-gray-500">Eligibility</span>
              <span className="font-medium text-gray-900 text-right">
                {opportunity.eligibility}
              </span>
            </div>

            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span className="text-gray-500">Stipend / Reward</span>
              <span className="font-medium text-gray-900">
                {opportunity.stipend}
              </span>
            </div>
          </div>

          <div className="mt-6">
            <a
              href={opportunity.sourceLink}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-gray-900 text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors"
            >
              View source
            </a>
          </div>
        </div>
      </div>
    </main>
  );
}