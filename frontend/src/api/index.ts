const API_BASE = "http://localhost:8000";

export interface UserInput {
  city: string;
  skills: string[];
  available_time: string;
  risk_preference: string;
  avoid_appearing: boolean;
  monthly_goal: number;
}

export interface AppConfig {
  llm_provider: string;
  llm_api_key: string;
  llm_model: string;
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

export async function getConfig(): Promise<AppConfig> {
  const response = await fetch(`${API_BASE}/api/config`);
  if (!response.ok) throw new Error("获取配置失败");
  return response.json();
}

export async function saveConfig(config: AppConfig): Promise<void> {
  const response = await fetch(`${API_BASE}/api/config`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(config),
  });
  if (!response.ok) throw new Error("保存配置失败");
}

export async function getModels(provider: string): Promise<string[]> {
  const response = await fetch(`${API_BASE}/api/models?provider=${provider}`);
  if (!response.ok) return [];
  return response.json();
}