export type Opportunity = {
  id: string;
  title: string;
  organization: string;
  category: "Hackathon" | "Internship" | "Scholarship" | "Fellowship" | "Course" | "Government Scheme";
  deadline: string; // ISO date string
  eligibility: string;
  stipend: string;
  sourceLink: string;
  confidenceScore: number; // 0 to 1
};

export const mockOpportunities: Opportunity[] = [
  {
    id: "1",
    title: "Build with Bharat 2.0",
    organization: "NIT Delhi",
    category: "Hackathon",
    deadline: "2026-09-15",
    eligibility: "Open to all college students",
    stipend: "Prizes up to ₹50,000",
    sourceLink: "https://example.com/build-with-bharat",
    confidenceScore: 0.95,
  },
  {
    id: "2",
    title: "PM Internship Scheme",
    organization: "Ministry of Corporate Affairs",
    category: "Government Scheme",
    deadline: "2026-09-30",
    eligibility: "Ages 21-24, not currently employed full-time",
    stipend: "₹5,000/month",
    sourceLink: "https://pminternship.mca.gov.in",
    confidenceScore: 0.9,
  },
  {
    id: "3",
    title: "National Scholarship Portal - Merit Scholarship",
    organization: "Government of India",
    category: "Scholarship",
    deadline: "2026-10-05",
    eligibility: "Students with family income below ₹8 LPA",
    stipend: "₹12,000/year",
    sourceLink: "https://scholarships.gov.in",
    confidenceScore: 0.6,
  },
  {
    id: "4",
    title: "Summer AI Fellowship",
    organization: "TechCorp",
    category: "Fellowship",
    deadline: "2026-09-20",
    eligibility: "Final year CS students",
    stipend: "₹25,000/month",
    sourceLink: "https://example.com/ai-fellowship",
    confidenceScore: 0.8,
  },
];