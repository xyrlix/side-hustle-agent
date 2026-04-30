import { useState, useEffect } from "react";
import { getConfig, saveConfig, UserInput, RecommendationResult, AppConfig, getAnalyticsSummary, getToken } from "./api";
import UserForm from "./components/UserForm";
import ResultCard from "./components/ResultCard";
import LoadingSpinner from "./components/LoadingSpinner";
import ConfigModal from "./components/ConfigModal";
import LoginModal from "./components/LoginModal";
import AdminPanel from "./components/AdminPanel";
import ContentManager from "./components/ContentManager";
import AnalyticsDashboard from "./components/AnalyticsDashboard";
import MaterialManager from "./components/MaterialManager";
import PlatformManager from "./components/PlatformManager";
import ScheduledPostsManager from "./components/ScheduledPostsManager";
import HotTopicsPanel from "./components/HotTopicsPanel";
import ContentCheckPanel from "./components/ContentCheckPanel";
import ROIAnalysisPanel from "./components/ROIAnalysisPanel";

type Page = "dashboard" | "hustle" | "content" | "analytics" | "platforms" | "materials" | "scheduled" | "hottopics" | "check" | "roi";
type Role = "admin" | "owner" | "editor" | "viewer" | "guest";

interface User {
  id: number;
  username: string;
  role: Role;
}

// ============ 权限配置 ============
const ROLE_PERMISSIONS: Record<Role, Page[]> = {
  guest: ["dashboard"],
  viewer: ["dashboard", "analytics", "hottopics", "check", "roi"],
  editor: ["dashboard", "hustle", "content", "materials", "hottopics", "check", "roi"],
  owner: ["dashboard", "hustle", "content", "analytics", "platforms", "materials", "scheduled", "hottopics", "check", "roi"],
  admin: ["dashboard", "hustle", "content", "analytics", "platforms", "materials", "scheduled", "hottopics", "check", "roi"],
};

// 页面信息
const PAGE_INFO: Record<Page, { title: string; icon: string; section: string; desc: string; roles: Role[] }> = {
  dashboard: { title: "工作台", icon: "📊", section: "main", desc: "查看整体运营状况", roles: ["guest", "viewer", "editor", "owner", "admin"] },
  hustle: { title: "副业推荐", icon: "🎯", section: "analyze", desc: "AI 智能分析您的最佳副业方向", roles: ["editor", "owner", "admin"] },
  content: { title: "内容管理", icon: "📝", section: "create", desc: "创建、编辑、发布内容", roles: ["editor", "owner", "admin"] },
  analytics: { title: "数据分析", icon: "📈", section: "data", desc: "查看内容运营数据", roles: ["viewer", "owner", "admin"] },
  platforms: { title: "平台管理", icon: "🔗", section: "publish", desc: "管理社交媒体平台账号", roles: ["owner", "admin"] },
  materials: { title: "素材库", icon: "📦", section: "create", desc: "管理图片、视频等素材", roles: ["editor", "owner", "admin"] },
  scheduled: { title: "定时发布", icon: "⏰", section: "publish", desc: "管理定时发布任务", roles: ["owner", "admin"] },
  hottopics: { title: "热点话题", icon: "🔥", section: "create", desc: "追踪各平台热点话题", roles: ["viewer", "editor", "owner", "admin"] },
  check: { title: "内容检测", icon: "🔍", section: "create", desc: "检测违规词和限流风险", roles: ["viewer", "editor", "owner", "admin"] },
  roi: { title: "ROI分析", icon: "💹", section: "data", desc: "投资回报率分析", roles: ["viewer", "editor", "owner", "admin"] },
};

// 工作流分组
const WORKFLOW_SECTIONS = [
  { id: "main", label: "工作台", items: ["dashboard"] as Page[], roles: ["guest", "viewer", "editor", "owner", "admin"] },
  { id: "analyze", label: "副业分析", items: ["hustle"] as Page[], roles: ["editor", "owner", "admin"] },
  { id: "create", label: "内容创作", items: ["content", "materials", "hottopics", "check"] as Page[], roles: ["editor", "owner", "admin"] },
  { id: "publish", label: "发布管理", items: ["platforms", "scheduled"] as Page[], roles: ["owner", "admin"] },
  { id: "data", label: "数据分析", items: ["analytics", "roi"] as Page[], roles: ["viewer", "editor", "owner", "admin"] },
];

// ============ 公共登录页 ============
function PublicLanding({ onLogin }: { onLogin: () => void }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-700 flex items-center justify-center p-8">
      <div className="max-w-4xl w-full">
        {/* Logo 和标题 */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-24 h-24 bg-white/20 rounded-3xl backdrop-blur mb-6">
            <span className="text-5xl">📡</span>
          </div>
          <h1 className="text-5xl font-bold text-white mb-4">副业雷达</h1>
          <p className="text-2xl text-white/80">多平台社交媒体内容管理系统</p>
        </div>

        {/* 功能介绍 */}
        <div className="grid grid-cols-3 gap-6 mb-12">
          <div className="bg-white/10 backdrop-blur rounded-2xl p-6 border border-white/20">
            <div className="w-14 h-14 bg-violet-500/30 rounded-xl flex items-center justify-center text-3xl mb-4">🎯</div>
            <h3 className="text-xl font-bold text-white mb-2">AI 副业推荐</h3>
            <p className="text-white/70">多智能体协同分析，匹配最适合您的副业方向</p>
          </div>
          <div className="bg-white/10 backdrop-blur rounded-2xl p-6 border border-white/20">
            <div className="w-14 h-14 bg-emerald-500/30 rounded-xl flex items-center justify-center text-3xl mb-4">📝</div>
            <h3 className="text-xl font-bold text-white mb-2">内容管理</h3>
            <p className="text-white/70">创建、编辑、多平台发布，一站式内容运营</p>
          </div>
          <div className="bg-white/10 backdrop-blur rounded-2xl p-6 border border-white/20">
            <div className="w-14 h-14 bg-sky-500/30 rounded-xl flex items-center justify-center text-3xl mb-4">📊</div>
            <h3 className="text-xl font-bold text-white mb-2">数据分析</h3>
            <p className="text-white/70">运营数据统计、ROI 分析，优化内容策略</p>
          </div>
        </div>

        {/* 登录按钮 */}
        <div className="text-center">
          <button
            onClick={onLogin}
            className="px-12 py-5 bg-white text-purple-700 rounded-2xl font-bold text-xl hover:bg-white/90 transition-all shadow-2xl shadow-purple-500/30"
          >
            🔐 登录系统
          </button>
          <p className="text-white/60 mt-4 text-lg">登录后解锁全部功能</p>
        </div>

        {/* 默认账号提示 */}
        <div className="mt-8 text-center text-white/50 text-base">
          默认管理员: admin / admin123
        </div>
      </div>
    </div>
  );
}

// ============ 仪表板组件 ============
function Dashboard({ user, onNavigate }: { user: User; onNavigate: (page: Page) => void }) {
  const [stats, setStats] = useState<any>(null);
  const { role } = user;

  useEffect(() => { loadStats(); }, []);

  const loadStats = async () => {
    try {
      const res = await getAnalyticsSummary();
      if (res.success) setStats(res.summary);
    } catch (e) { console.error("加载统计失败:", e); }
  };

  const canSee = (page: Page) => ROLE_PERMISSIONS[role].includes(page);

  return (
    <div className="space-y-8">
      {/* 欢迎区块 */}
      <div className="bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 rounded-2xl p-10 shadow-xl shadow-purple-500/20">
        <h2 className="text-4xl font-bold text-white mb-3">欢迎回来，{user.username}</h2>
        <p className="text-white/80 text-xl mb-6">
          {role === "admin" && "管理员身份 · 拥有全部权限"}
          {role === "owner" && "所有者身份 · 管理全部内容"}
          {role === "editor" && "编辑身份 · 创建和发布内容"}
          {role === "viewer" && "查看者身份 · 仅可查看数据"}
        </p>
        <div className="flex gap-4">
          {canSee("hustle") && (
            <button
              onClick={() => onNavigate("hustle")}
              className="px-8 py-4 bg-white text-purple-700 rounded-xl font-semibold text-lg hover:bg-white/90 transition-all shadow-lg flex items-center gap-3"
            >
              <span className="text-2xl">🎯</span> 副业推荐
            </button>
          )}
          {canSee("content") && (
            <button
              onClick={() => onNavigate("content")}
              className="px-8 py-4 bg-white/20 text-white rounded-xl font-semibold text-lg hover:bg-white/30 transition-all border border-white/30 flex items-center gap-3"
            >
              <span className="text-2xl">📝</span> 内容管理
            </button>
          )}
          {canSee("analytics") && (
            <button
              onClick={() => onNavigate("analytics")}
              className="px-8 py-4 bg-white/20 text-white rounded-xl font-semibold text-lg hover:bg-white/30 transition-all border border-white/30 flex items-center gap-3"
            >
              <span className="text-2xl">📊</span> 数据分析
            </button>
          )}
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-4 gap-6">
        <StatCard icon="📊" label="内容总数" value={stats?.total_content || 0} color="purple" />
        <StatCard icon="✅" label="已发布" value={stats?.published || 0} color="emerald" />
        <StatCard icon="👁️" label="总阅读量" value={stats?.total_views || 0} color="sky" />
        <StatCard icon="💰" label="总收益" value={`¥${stats?.total_revenue || 0}`} color="amber" />
      </div>

      {/* 快捷入口 */}
      <div>
        <h3 className="text-2xl font-bold text-gray-900 mb-6">快捷操作</h3>
        <div className="grid grid-cols-5 gap-5">
          {canSee("hustle") && <QuickAction icon="🎯" title="副业推荐" desc="AI智能分析匹配" onClick={() => onNavigate("hustle")} color="violet" />}
          {canSee("content") && <QuickAction icon="📝" title="内容管理" desc="创建发布内容" onClick={() => onNavigate("content")} color="cyan" />}
          {canSee("analytics") && <QuickAction icon="📈" title="数据分析" desc="查看运营报表" onClick={() => onNavigate("analytics")} color="emerald" />}
          {canSee("hottopics") && <QuickAction icon="🔥" title="热点话题" desc="追踪热门内容" onClick={() => onNavigate("hottopics")} color="orange" />}
          {canSee("roi") && <QuickAction icon="💹" title="ROI分析" desc="效益投资回报" onClick={() => onNavigate("roi")} color="rose" />}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color }: { icon: string; label: string; value: number | string; color: string }) {
  const colors: Record<string, { bg: string; border: string; text: string; icon: string }> = {
    purple: { bg: "bg-violet-50", border: "border-violet-200", text: "text-violet-700", icon: "text-violet-500" },
    emerald: { bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-700", icon: "text-emerald-500" },
    sky: { bg: "bg-sky-50", border: "border-sky-200", text: "text-sky-700", icon: "text-sky-500" },
    amber: { bg: "bg-amber-50", border: "border-amber-200", text: "text-amber-700", icon: "text-amber-500" },
  };
  const c = colors[color] || colors.purple;

  return (
    <div className={`p-6 rounded-2xl bg-white border-2 ${c.border} shadow-sm`}>
      <div className="flex items-center gap-4">
        <div className={`w-14 h-14 rounded-xl ${c.bg} border border-transparent flex items-center justify-center ${c.icon}`}>
          <span className="text-3xl">{icon}</span>
        </div>
        <div>
          <div className={`text-3xl font-bold ${c.text}`}>{value}</div>
          <div className="text-gray-500 text-lg font-medium mt-1">{label}</div>
        </div>
      </div>
    </div>
  );
}

function QuickAction({ icon, title, desc, onClick, color }: { icon: string; title: string; desc: string; onClick: () => void; color: string }) {
  const colorMap: Record<string, { bg: string; border: string; hover: string; icon: string }> = {
    violet: { bg: "bg-violet-50", border: "border-violet-200", hover: "hover:bg-violet-100", icon: "text-violet-600" },
    cyan: { bg: "bg-cyan-50", border: "border-cyan-200", hover: "hover:bg-cyan-100", icon: "text-cyan-600" },
    emerald: { bg: "bg-emerald-50", border: "border-emerald-200", hover: "hover:bg-emerald-100", icon: "text-emerald-600" },
    orange: { bg: "bg-orange-50", border: "border-orange-200", hover: "hover:bg-orange-100", icon: "text-orange-600" },
    rose: { bg: "bg-rose-50", border: "border-rose-200", hover: "hover:bg-rose-100", icon: "text-rose-600" },
  };
  const c = colorMap[color] || colorMap.violet;

  return (
    <button
      onClick={onClick}
      className={`p-6 rounded-2xl bg-white border-2 ${c.border} text-left transition-all ${c.hover} group shadow-sm`}
    >
      <div className={`w-14 h-14 rounded-xl ${c.bg} flex items-center justify-center mb-4 ${c.icon} group-hover:scale-110 transition-transform`}>
        <span className="text-3xl">{icon}</span>
      </div>
      <div className="text-gray-900 font-bold text-xl mb-1">{title}</div>
      <div className="text-gray-500 text-base">{desc}</div>
    </button>
  );
}

// ============ 副业推荐页面 ============
function HustlePage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RecommendationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (input: UserInput) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("http://localhost:8000/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
      });
      setResult(await res.json());
    } catch {
      setError("请求失败，请检查后端服务是否启动");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Hero Form */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
        <div className="bg-gradient-to-r from-violet-600 to-purple-600 p-8">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-14 h-14 rounded-xl bg-white/20 flex items-center justify-center">
              <span className="text-3xl">📡</span>
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white">开始智能匹配</h2>
              <p className="text-white/70 text-lg mt-1">填写信息，多智能体协同分析您的最佳副业方向</p>
            </div>
          </div>
        </div>
        <div className="p-8">
          <UserForm onSubmit={handleSubmit} disabled={loading} />
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-16 text-center">
          <LoadingSpinner />
          <p className="text-gray-600 text-2xl font-medium mt-8">深度分析中...</p>
          <p className="text-gray-400 text-lg mt-2">多智能体协同推理 · 请稍候</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-8 text-red-600 text-xl text-center font-medium">
          {error}
        </div>
      )}

      {/* Results */}
      {result?.success && result.data && (
        <div className="space-y-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-emerald-100 flex items-center justify-center text-3xl">🎯</div>
            <div>
              <h2 className="text-3xl font-bold text-gray-900">为您推荐</h2>
              <p className="text-gray-500 text-lg">基于深度画像分析生成</p>
            </div>
          </div>
          <ResultCard data={result.data} />
        </div>
      )}

      {result && !result.success && (
        <div className="bg-amber-50 border-2 border-amber-200 rounded-2xl p-8 text-amber-600 text-xl text-center font-medium">
          {result.message}
        </div>
      )}
    </div>
  );
}

// ============ 访问拒绝页 ============
function AccessDenied({ onBack }: { onBack: () => void }) {
  return (
    <div className="flex items-center justify-center h-96">
      <div className="text-center">
        <div className="text-8xl mb-6">🔒</div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">权限不足</h2>
        <p className="text-xl text-gray-500 mb-8">您没有权限访问此页面</p>
        <button
          onClick={onBack}
          className="px-8 py-3 bg-violet-600 text-white rounded-xl font-semibold hover:bg-violet-700 transition-all"
        >
          返回工作台
        </button>
      </div>
    </div>
  );
}

// ============ 主应用 ============
export default function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [showConfig, setShowConfig] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [showAdmin, setShowAdmin] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    getConfig().then(setConfig).catch(() => {});
    const storedUser = localStorage.getItem("auth_user");
    if (storedUser) {
      try {
        const parsed = JSON.parse(storedUser);
        // 确保 role 是有效的
        const validRoles: Role[] = ["admin", "owner", "editor", "viewer", "guest"];
        const userWithValidRole: User = {
          id: parsed.id,
          username: parsed.username,
          role: validRoles.includes(parsed.role) ? parsed.role : "viewer"
        };
        setCurrentUser(userWithValidRole);
      } catch (e) {
        console.error("解析用户失败:", e);
        localStorage.removeItem("auth_user");
        localStorage.removeItem("auth_token");
      }
    }
  }, []);

  // 权限检查
  const canAccess = (targetPage: Page): boolean => {
    if (!currentUser) return targetPage === "dashboard";
    return ROLE_PERMISSIONS[currentUser.role].includes(targetPage);
  };

  const handleNavigate = (targetPage: Page) => {
    if (canAccess(targetPage)) {
      setPage(targetPage);
    } else {
      // 重定向到 dashboard
      setPage("dashboard");
    }
  };

  const handleLogin = async (_token: string, user: any) => {
    const userWithRole: User = { ...user, role: (user.role as Role) || "viewer" };
    setCurrentUser(userWithRole);
    setShowLogin(false);
  };

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("auth_user");
    setCurrentUser(null);
    setPage("dashboard");
  };

  const handleSaveConfig = async (newConfig: AppConfig) => {
    try { await saveConfig(newConfig); setConfig(newConfig); setShowConfig(false); } catch { alert("保存配置失败"); }
  };

  // 未登录显示公共页面
  if (!currentUser) {
    return (
      <>
        <PublicLanding onLogin={() => setShowLogin(true)} />
        {showLogin && <LoginModal onClose={() => setShowLogin(false)} onLogin={handleLogin} />}
      </>
    );
  }

  const { role } = currentUser;
  const currentPageInfo = PAGE_INFO[page];
  const isSubPage = page !== "dashboard";
  const token = getToken() || "";

  // 过滤当前角色可访问的导航项
  const visibleSections = WORKFLOW_SECTIONS.filter(section => section.roles.includes(role));

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* 侧边栏 - 白色系 */}
      <aside className={`${sidebarOpen ? 'w-72' : 'w-20'} bg-white border-r border-gray-200 flex flex-col transition-all duration-300 sticky top-0 h-screen`}>
        {/* Logo */}
        <div className="p-5 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-600 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-purple-500/30">
              <span className="text-2xl">📡</span>
            </div>
            {sidebarOpen && (
              <div>
                <h1 className="text-xl font-bold text-gray-900">副业雷达</h1>
                <p className="text-gray-400 text-sm">多平台管理</p>
              </div>
            )}
          </div>
        </div>

        {/* 导航列表 */}
        <nav className="flex-1 p-4 overflow-y-auto">
          {visibleSections.map((section) => (
            <div key={section.id} className="mb-6">
              {sidebarOpen && (
                <div className="text-xs font-bold text-gray-300 uppercase tracking-wider px-3 mb-3">
                  {section.label}
                </div>
              )}
              <div className="space-y-1">
                {section.items.map((item) => {
                  const info = PAGE_INFO[item];
                  const isActive = page === item;
                  return (
                    <button
                      key={item}
                      onClick={() => handleNavigate(item)}
                      className={`w-full px-4 py-3 rounded-xl text-left flex items-center gap-3 transition-all ${
                        isActive
                          ? "bg-gradient-to-r from-violet-600 to-purple-600 text-white shadow-lg shadow-purple-500/30"
                          : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                      }`}
                    >
                      <span className="text-xl flex-shrink-0">{info.icon}</span>
                      {sidebarOpen && <span className="font-semibold text-lg">{info.title}</span>}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* 折叠按钮 */}
        <div className="p-4 border-t border-gray-100">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-full px-4 py-3 rounded-xl text-gray-400 hover:text-gray-600 hover:bg-gray-50 transition-all flex items-center justify-center gap-2 text-lg"
          >
            <span>{sidebarOpen ? '◀' : '▶'}</span>
            {sidebarOpen && <span className="font-medium">收起</span>}
          </button>
        </div>
      </aside>

      {/* 主内容区 */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* 顶部栏 */}
        <header className="bg-white border-b border-gray-200 px-8 py-5 sticky top-0 z-40 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              {/* 面包屑 */}
              <div className="flex items-center gap-2 text-lg text-gray-400 mb-2">
                <button onClick={() => setPage("dashboard")} className="hover:text-gray-600 transition-colors">工作台</button>
                {isSubPage && (
                  <>
                    <span>›</span>
                    <span className="text-gray-500">
                      {currentPageInfo.section === 'analyze' ? '副业分析' :
                       currentPageInfo.section === 'create' ? '内容创作' :
                       currentPageInfo.section === 'publish' ? '发布管理' :
                       currentPageInfo.section === 'data' ? '数据分析' : ''}
                    </span>
                    <span>›</span>
                    <span className="text-gray-900 font-semibold">{currentPageInfo.title}</span>
                  </>
                )}
              </div>
              {/* 页面标题 */}
              <h2 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <span className="text-3xl">{currentPageInfo.icon}</span>
                <span>{currentPageInfo.title}</span>
              </h2>
            </div>

            {/* 用户操作 */}
            <div className="flex items-center gap-4">
              {/* 角色标签 */}
              <div className={`px-4 py-2 rounded-xl text-sm font-bold ${
                role === "admin" ? "bg-red-100 text-red-700" :
                role === "owner" ? "bg-violet-100 text-violet-700" :
                role === "editor" ? "bg-emerald-100 text-emerald-700" :
                "bg-gray-100 text-gray-600"
              }`}>
                {role === "admin" ? "管理员" :
                 role === "owner" ? "所有者" :
                 role === "editor" ? "编辑" : "查看者"}
              </div>

              <div className="text-gray-600 text-lg">
                <span className="font-semibold text-violet-600">{currentUser.username}</span>
              </div>
              {role === "admin" && (
                <button onClick={() => setShowAdmin(true)} className="px-5 py-2.5 bg-violet-100 text-violet-700 rounded-xl font-semibold hover:bg-violet-200 transition-all">
                  管理
                </button>
              )}
              <button onClick={() => setShowConfig(true)} className="px-5 py-2.5 bg-gray-100 text-gray-600 rounded-xl font-semibold hover:bg-gray-200 transition-all">
                ⚙️ 设置
              </button>
              <button onClick={handleLogout} className="px-5 py-2.5 bg-gray-100 text-gray-600 rounded-xl font-semibold hover:bg-gray-200 transition-all">
                退出
              </button>
            </div>
          </div>
        </header>

        {/* 页面描述 */}
        {isSubPage && (
          <div className="px-8 py-4 bg-gray-50 border-b border-gray-100">
            <p className="text-lg text-gray-500">{currentPageInfo.desc}</p>
          </div>
        )}

        {/* 主内容 */}
        <main className="flex-1 p-8 bg-gray-100 overflow-y-auto">
          {page === "dashboard" && <Dashboard user={currentUser} onNavigate={setPage} />}
          {page === "hustle" && canAccess("hustle") && <HustlePage />}
          {page === "content" && canAccess("content") && <ContentManager token={token} onBack={() => setPage("dashboard")} />}
          {page === "analytics" && canAccess("analytics") && <AnalyticsDashboard token={token} onBack={() => setPage("dashboard")} />}
          {page === "platforms" && canAccess("platforms") && <PlatformManager token={token} onBack={() => setPage("dashboard")} />}
          {page === "materials" && canAccess("materials") && <MaterialManager token={token} onBack={() => setPage("dashboard")} />}
          {page === "scheduled" && canAccess("scheduled") && <ScheduledPostsManager token={token} onBack={() => setPage("dashboard")} />}
          {page === "hottopics" && canAccess("hottopics") && <HotTopicsPanel token={token} onBack={() => setPage("dashboard")} />}
          {page === "check" && canAccess("check") && <ContentCheckPanel token={token} onBack={() => setPage("dashboard")} />}
          {page === "roi" && canAccess("roi") && <ROIAnalysisPanel token={token} onBack={() => setPage("dashboard")} />}

          {/* 访问被拒绝 */}
          {!canAccess(page) && page !== "dashboard" && (
            <AccessDenied onBack={() => setPage("dashboard")} />
          )}
        </main>
      </div>

      {/* Modals */}
      {showConfig && <ConfigModal config={config} onSave={handleSaveConfig} onClose={() => setShowConfig(false)} />}
      {showLogin && <LoginModal onClose={() => setShowLogin(false)} onLogin={handleLogin} />}
      {showAdmin && <AdminPanel onClose={() => setShowAdmin(false)} />}
    </div>
  );
}