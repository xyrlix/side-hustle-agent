const API_BASE = "http://localhost:8000";

export interface UserInput {
  city: string;
  skills: string[];
  available_time: string;
  risk_preference: string;
  avoid_appearing: boolean;
  monthly_goal: number;
  employment_status: string;
  industry: string;
  work_experience: string;
  side_hustle_exp: string;
  startup_budget: string;
  work_mode: string;
}

export interface AppConfig {
  llm_provider: string;
  llm_api_key: string;
  llm_model: string;
}

export interface User {
  id: number;
  username: string;
  role: string;
}

export interface AuthResult {
  success: boolean;
  token?: string;
  user?: User;
  message?: string;
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

// ============ Auth ============

export async function login(username: string, password: string): Promise<AuthResult> {
  const formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);
  const response = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  return response.json();
}

export async function register(username: string, password: string, email: string = ""): Promise<AuthResult> {
  const response = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, email }),
  });
  return response.json();
}

export async function getMe(): Promise<AuthResult> {
  const token = localStorage.getItem("auth_token");
  if (!token) return { success: false, message: "未登录" };
  const response = await fetch(`${API_BASE}/api/auth/me`, {
    headers: { "Authorization": `Bearer ${token}` },
  });
  return response.json();
}

export function getToken(): string | null {
  return localStorage.getItem("auth_token");
}

export function setToken(token: string) {
  localStorage.setItem("auth_token", token);
}

export function removeToken() {
  localStorage.removeItem("auth_token");
}

// ============ Recommendations ============

export async function getRecommendation(input: UserInput): Promise<RecommendationResult> {
  const token = getToken();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}/api/recommend`, {
    method: "POST",
    headers,
    body: JSON.stringify(input),
  });
  return response.json();
}

export async function getHistory(): Promise<any> {
  const token = getToken();
  if (!token) return { success: false, message: "未登录" };
  const response = await fetch(`${API_BASE}/api/history`, {
    headers: { "Authorization": `Bearer ${token}` },
  });
  return response.json();
}

// ============ Admin ============

export async function getAdminStats(): Promise<any> {
  const token = getToken();
  const response = await fetch(`${API_BASE}/api/admin/stats`, {
    headers: { "Authorization": `Bearer ${token}` },
  });
  return response.json();
}

export async function getAdminUsers(): Promise<any> {
  const token = getToken();
  const response = await fetch(`${API_BASE}/api/admin/users`, {
    headers: { "Authorization": `Bearer ${token}` },
  });
  return response.json();
}

export async function getAdminRecommendations(limit: number = 100): Promise<any> {
  const token = getToken();
  const response = await fetch(`${API_BASE}/api/admin/recommendations?limit=${limit}`, {
    headers: { "Authorization": `Bearer ${token}` },
  });
  return response.json();
}

export async function getAdminHustleStats(): Promise<any> {
  const token = getToken();
  const response = await fetch(`${API_BASE}/api/admin/hustle_stats`, {
    headers: { "Authorization": `Bearer ${token}` },
  });
  return response.json();
}

export async function getAdminUserProfiles(): Promise<any> {
  const token = getToken();
  const response = await fetch(`${API_BASE}/api/admin/user_profiles`, {
    headers: { "Authorization": `Bearer ${token}` },
  });
  return response.json();
}

// ============ Config ============

export async function getConfig(): Promise<AppConfig> {
  const response = await fetch(`${API_BASE}/api/config`);
  if (!response.ok) throw new Error("获取配置失败");
  return response.json();
}

export async function saveConfig(config: AppConfig): Promise<void> {
  const response = await fetch(`${API_BASE}/api/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  if (!response.ok) throw new Error("保存配置失败");
}

export async function getModels(provider: string): Promise<string[]> {
  const response = await fetch(`${API_BASE}/api/models?provider=${provider}`);
  if (!response.ok) return [];
  return response.json();
}

// ============ Content Management ============

export interface ContentItem {
  id: number;
  title: string;
  summary: string;
  body: string;
  status: string;
  tags: string[];
  category: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  revenue: number;
  platform_versions: Record<string, string>;
  published_platforms: string[];
  scheduled_at: string | null;
  published_at: string | null;
  ai_generated: boolean;
  ai_prompt: string;
  created_at: string;
  updated_at: string;
}

export interface Platform {
  id: string;
  name: string;
  content_format: string[];
  max_content_length: number;
  features: string[];
}

export interface PublishLog {
  id: number;
  platform: string;
  status: string;
  error_message: string;
  published_url: string;
  published_at: string;
  created_at: string;
}

export interface AnalyticsSummary {
  total_content: number;
  published: number;
  drafts: number;
  pending: number;
  total_views: number;
  total_likes: number;
  total_revenue: number;
}

export interface ContentListResponse {
  success: boolean;
  contents: ContentItem[];
  total: number;
}

export interface ContentResponse {
  success: boolean;
  content: ContentItem;
  message?: string;
}

export interface PlatformListResponse {
  success: boolean;
  platforms: Platform[];
}

export interface AnalyticsResponse {
  success: boolean;
  summary: AnalyticsSummary;
}

async function contentRequest(url: string, options: RequestInit = {}): Promise<any> {
  const token = getToken();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return fetch(url, { ...options, headers }).then(r => r.json());
}

export async function createContent(data: {
  title: string;
  body?: string;
  summary?: string;
  cover_image?: string;
  tags?: string[];
  category?: string;
  ai_generated?: boolean;
  ai_prompt?: string;
}): Promise<ContentResponse> {
  return contentRequest(`${API_BASE}/api/content`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getContent(contentId: number): Promise<ContentResponse> {
  return contentRequest(`${API_BASE}/api/content/${contentId}`);
}

export async function getContents(status?: string, limit = 50, offset = 0): Promise<ContentListResponse> {
  let url = `${API_BASE}/api/content?limit=${limit}&offset=${offset}`;
  if (status) url += `&status=${status}`;
  return contentRequest(url);
}

export async function updateContent(contentId: number, data: Partial<{
  title: string;
  body: string;
  summary: string;
  cover_image: string;
  tags: string[];
  category: string;
  status: string;
  scheduled_at: string;
}>): Promise<ContentResponse> {
  return contentRequest(`${API_BASE}/api/content/${contentId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteContent(contentId: number): Promise<{ success: boolean; message: string }> {
  return contentRequest(`${API_BASE}/api/content/${contentId}`, {
    method: "DELETE",
  });
}

export async function getContentVersions(contentId: number): Promise<any> {
  return contentRequest(`${API_BASE}/api/content/${contentId}/versions`);
}

export async function publishContent(contentId: number, platform: string): Promise<any> {
  return contentRequest(`${API_BASE}/api/content/${contentId}/publish?platform=${platform}`, {
    method: "POST",
  });
}

export async function getPublishLogs(contentId: number): Promise<{ success: boolean; logs: PublishLog[] }> {
  return contentRequest(`${API_BASE}/api/content/${contentId}/logs`);
}

export async function getPlatforms(): Promise<PlatformListResponse> {
  return fetch(`${API_BASE}/api/platforms`).then(r => r.json());
}

export async function getAnalyticsSummary(): Promise<AnalyticsResponse> {
  return contentRequest(`${API_BASE}/api/analytics/summary`);
}

// ============ Campaign Management ============

export interface Campaign {
  id: number;
  name: string;
  description: string;
  content_ids: number[];
  start_date: string | null;
  end_date: string | null;
  target_views: number;
  target_revenue: number;
  actual_views: number;
  actual_revenue: number;
  status: string;
  created_at: string;
}

export async function createCampaign(data: { name: string; description?: string; start_date?: string; end_date?: string }): Promise<any> {
  return contentRequest(`${API_BASE}/api/campaigns`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getCampaigns(limit = 50): Promise<{ success: boolean; campaigns: Campaign[] }> {
  return contentRequest(`${API_BASE}/api/campaigns?limit=${limit}`);
}

export async function addContentToCampaign(campaignId: number, contentId: number): Promise<any> {
  return contentRequest(`${API_BASE}/api/campaigns/${campaignId}/content?content_id=${contentId}`, {
    method: "POST",
  });
}

// ============ Platform Accounts ============

export interface PlatformAccount {
  id: number;
  platform: string;
  account_name: string;
  account_id: string;
  status: string;
  followers: number;
  created_at: string;
  updated_at: string;
}

export async function createPlatformAccount(data: {
  platform: string;
  account_name: string;
  account_id?: string;
  access_token?: string;
  refresh_token?: string;
}): Promise<any> {
  return contentRequest(`${API_BASE}/api/platforms/accounts`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getPlatformAccounts(): Promise<{ success: boolean; accounts: PlatformAccount[] }> {
  return contentRequest(`${API_BASE}/api/platforms/accounts`);
}

export async function updatePlatformAccount(accountId: number, data: Partial<{ followers: number; status: string }>): Promise<any> {
  return contentRequest(`${API_BASE}/api/platforms/accounts/${accountId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deletePlatformAccount(accountId: number): Promise<{ success: boolean; message: string }> {
  return contentRequest(`${API_BASE}/api/platforms/accounts/${accountId}`, {
    method: "DELETE",
  });
}

// ============ Analytics ============

export async function getAnalytics(platform?: string, days = 30): Promise<any> {
  let url = `${API_BASE}/api/analytics?days=${days}`;
  if (platform) url += `&platform=${platform}`;
  return contentRequest(url);
}

export async function getAnalyticsSummaryFull(): Promise<any> {
  return contentRequest(`${API_BASE}/api/analytics/summary`);
}

export async function createAnalytics(data: {
  platform: string;
  date: string;
  views?: number;
  likes?: number;
  comments?: number;
  shares?: number;
  followers?: number;
  revenue?: number;
}): Promise<any> {
  return contentRequest(`${API_BASE}/api/analytics`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ============ Scheduled Posts ============

export interface ScheduledPost {
  id: number;
  content_id: number;
  platform: string;
  scheduled_at: string;
  status: string;
  created_at: string;
}

export async function createScheduledPost(data: {
  content_id: number;
  platform: string;
  scheduled_at: string;
}): Promise<any> {
  return contentRequest(`${API_BASE}/api/scheduled-posts`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getScheduledPosts(status?: string): Promise<{ success: boolean; scheduled_posts: ScheduledPost[] }> {
  let url = `${API_BASE}/api/scheduled-posts`;
  if (status) url += `?status=${status}`;
  return contentRequest(url);
}

export async function cancelScheduledPost(postId: number): Promise<any> {
  return contentRequest(`${API_BASE}/api/scheduled-posts/${postId}`, {
    method: "DELETE",
  });
}

// ============ Materials ============

export interface Material {
  id: number;
  filename: string;
  file_path: string;
  file_type: string;
  mime_type: string;
  file_size: number;
  width?: number;
  height?: number;
  duration?: number;
  tags: string[];
  folder: string;
  created_at: string;
}

export async function getMaterials(file_type?: string, folder?: string): Promise<{ success: boolean; materials: Material[] }> {
  let url = `${API_BASE}/api/materials`;
  const params = new URLSearchParams();
  if (file_type) params.set("file_type", file_type);
  if (folder) params.set("folder", folder);
  const query = params.toString();
  if (query) url += `?${query}`;
  return contentRequest(url);
}

export async function deleteMaterial(materialId: number): Promise<any> {
  return contentRequest(`${API_BASE}/api/materials/${materialId}`, {
    method: "DELETE",
  });
}

// ============ OAuth ============

export async function getOAuthAuthorizeUrl(platform: string): Promise<any> {
  return contentRequest(`${API_BASE}/api/oauth/${platform}/authorize`);
}

export async function getOAuthPlatforms(): Promise<any> {
  return fetch(`${API_BASE}/api/oauth/platforms`).then(r => r.json());
}

// ============ RBAC ============

export async function getRoles(): Promise<any> {
  return contentRequest(`${API_BASE}/api/rbac/roles`);
}

export async function getPermissions(): Promise<any> {
  return contentRequest(`${API_BASE}/api/rbac/permissions`);
}

export async function getUserRoles(userId?: number): Promise<any> {
  let url = `${API_BASE}/api/rbac/user/roles`;
  if (userId) url += `?user_id=${userId}`;
  return contentRequest(url);
}

export async function assignRole(userId: number, role: string): Promise<any> {
  return contentRequest(`${API_BASE}/api/rbac/user/roles?user_id=${userId}&role=${role}`, {
    method: "POST",
  });
}