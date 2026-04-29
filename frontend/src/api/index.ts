const API_BASE = "http://localhost:8000";

export interface UserInput {
  city: string;
  skills: string[];
  available_time: string;
  risk_preference: string;
  avoid_appearing: boolean;
  monthly_goal: number;
}

export interface RecommendationResult {
  success: boolean;
  message: string;
  data?: {
    user_profile: any;
    recommendations: any[];
    selected_recommendation: any;
    action_plan: any;
    validation_result: any;
  };
}

export async function getRecommendation(input: UserInput): Promise<RecommendationResult> {
  const response = await fetch(`${API_BASE}/api/recommend`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });
  return response.json();
}
