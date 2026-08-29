const API_URL = process.env.NEXT_PUBLIC_API_URL;

export type Opportunity = {
    id: string;
    user_id: string;
    title: string;
    organization: string | null;
    category: "hackathon" | "internship" | "scholarship" | "fellowship" | "course" | "meetup" | "government_scheme" | "other";
    deadline: string | null;
    eligibility: string | null;
    stipend: string | null;
    source_type: "instagram" | "telegram" | "whatsapp" | "linkedin" | "link" | "manual";
    raw_source_url: string | null;
    deadline_source_url: string | null;
    deadline_source_label: string | null;
    confidence_score: number;
    extraction_stage: string | null;
    status: "needs_confirmation" | "active" | "expired" | "archived";
    google_calendar_event_id: string | null;
    created_at: string;
    tags: { id: string; name: string }[];
};

export type GovtScheme = {
    id: string;
    title: string;
    organization: string | null;
    source: string;
    category: string;
    deadline: string | null;
    url: string;
    description: string | null;
    scraped_at: string;
};

function authHeaders(token: string | null) {
    return token ? { Authorization: `Bearer ${token}` } : {};
}

// Note: /tracker still requires user_id as a query param (backend hasn't
// switched it to JWT-based auth yet) — so we pass both userId and token.
// Once backend updates /tracker to use get_current_user, we can drop userId here.

export async function getOpportunities(userId: string, token: string | null): Promise<Opportunity[]> {
    const res = await fetch(`${API_URL}/tracker?user_id=${userId}`, {
        headers: authHeaders(token),
    });
    if (!res.ok) throw new Error("Failed to fetch opportunities");
    return res.json();
}

export async function getOpportunity(id: string, token: string | null): Promise<Opportunity> {
    const res = await fetch(`${API_URL}/tracker/${id}`, {
        headers: authHeaders(token),
    });
    if (!res.ok) throw new Error("Failed to fetch opportunity");
    return res.json();
}

export async function confirmOpportunity(id: string, token: string | null): Promise<Opportunity> {
    const res = await fetch(`${API_URL}/tracker/${id}/confirm`, {
        method: "POST",
        headers: authHeaders(token),
    });
    if (!res.ok) throw new Error("Failed to confirm opportunity");
    return res.json();
}

export async function getGovtSchemes(): Promise<GovtScheme[]> {
    const res = await fetch(`${API_URL}/resources`);
    if (!res.ok) throw new Error("Failed to fetch govt schemes");
    return res.json();
}