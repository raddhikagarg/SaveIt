import OpportunityCard from "./components/OpportunityCard";
import { mockOpportunities } from "@/lib/mockData";

export default function Dashboard() {
  return (
    <main className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">SaveIt</h1>
        <p className="text-gray-500 mb-8">
          Your tracked opportunities, deadlines, and government schemes.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {mockOpportunities.map((opportunity) => (
            <OpportunityCard key={opportunity.id} opportunity={opportunity} />
          ))}
        </div>
      </div>
    </main>
  );
}