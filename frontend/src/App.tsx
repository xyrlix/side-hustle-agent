import { useState, useEffect } from "react";
import { getConfig, saveConfig, UserInput, RecommendationResult, AppConfig, getAnalyticsSummary, getToken } from "./api";
import UserForm from "./components/UserForm";
import ResultCard from "./components/ResultCard";
import LoadingSpinner from "./components/LoadingSpinner";
import ConfigModal from "./components/ConfigModal";
import HeroBackground from "./components/HeroBackground";
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

// 页面信息
const PAGE_INFO: Record<Page, { title: string; icon: string; section: string; desc: string }> = {
  dashboard: { title: "工作台", icon: "📊", section: "main", desc: "查看整体运营状况" },
  hustle: { title: "副业推荐", icon: "🎯", section: "analyze", desc: "AI 智能分析您的最佳副业方向" },
  content: { title: "内容管理", icon: "📝", section: "create", desc: "创建、编辑、发布内容" },
  analytics: { title: "数据分析", icon: "📈", section: "data", desc: "查看内容运营数据" },
  platforms: { title: "平台管理", icon: "🔗", section: "publish", desc: "管理社交媒体平台账号" },
  materials: { title: "素材库", icon: "📦", section: "create", desc: "管理图片、视频等素材" },
  scheduled: { title: "定时发布", icon: "⏰", section: "publish", desc: "管理定时发布任务" },
  hottopics: { title: "热点话题", icon: "🔥", section: "create", desc: "追踪各平台热点话题" },
  check: { title: "内容检测", icon: "🔍", section: "create", desc: "检测违规词和限流风险" },
  roi: { title: "ROI分析", icon: "💹", section: "data", desc: "投资回报率分析" },
};

// 工作流分组
const WORKFLOW_SECTIONS = [
  {
    id: "main",
    label: "工作台",
    items: ["dashboard"]
  },
  {
    id: "analyze",
    label: "副业分析",
    items: ["hustle"]
  },
  {
    id: "create",
    label: "内容创作",
    items: ["content", "materials", "hottopics", "check"]
  },
  {
    id: "publish",
    label: "发布管理",
    items: ["platforms", "scheduled"]
  },
  {
    id: "data",
    label: "数据分析",
    items: ["analytics", "roi"]
  },
];

// 仪表板组件
function Dashboard({ onNavigate }: { onNavigate: (page: Page) => void }) {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const res = await getAnalyticsSummary();
      if (res.success) setStats(res.summary);
    } catch (e) {
      console.error("加载统计失败:", e);
    }
  };

  return (
    <div className="space-y-6">
      {/* 欢迎区块 */}
      <div className="relative rounded-2xl overflow-hidden">
        <HeroBackground />
        <div className="relative z-10 p-8 bg-gradient-to-r from-purple-900/60 to-indigo-900/60 backdrop-blur-sm border border-white/10 rounded-2xl">
          <h2 className="text-3xl font-bold text-white">欢迎使用副业雷达</h2>
          <p className="text-white/60 text-lg mt-2">基于 AI 智能分析，为你匹配最适合的副业方向</p>
          <div className="flex gap-4 mt-6">
            <button
              onClick={() => onNavigate("hustle")}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium text-base flex items-center gap-2 transition-all shadow-lg shadow-purple-500/30"
            >
              <span>🎯</span> 开始副业推荐
            </button>
            <button
              onClick={() => onNavigate("content")}
              className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl font-medium text-base flex items-center gap-2 transition-all border border-white/20"
            >
              <span>📝</span> 内容管理
            </button>
          </div>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-4 gap-5">
        <StatCard icon="📊" label="内容总数" value={stats?.total_content || 0} color="purple" />
        <StatCard icon="✅" label="已发布" value={stats?.published || 0} color="green" />
        <StatCard icon="👁️" label="总阅读量" value={stats?.total_views || 0} color="blue" />
        <StatCard icon="💰" label="总收益" value={`¥${stats?.total_revenue || 0}`} color="yellow" />
      </div>

      {/* 快捷入口 */}
      <div>
        <h3 className="text-lg font-semibold text-white/80 mb-4">快捷操作</h3>
        <div className="grid grid-cols-5 gap-4">
          <QuickAction icon="🎯" title="副业推荐" desc="AI智能分析" onClick={() => onNavigate("hustle")} color="purple" />
          <QuickAction icon="📝" title="内容管理" desc="创建内容" onClick={() => onNavigate("content")} color="cyan" />
          <QuickAction icon="📈" title="数据分析" desc="查看报表" onClick={() => onNavigate("analytics")} color="green" />
          <QuickAction icon="🔥" title="热点话题" desc="追踪热点" onClick={() => onNavigate("hottopics")} color="orange" />
          <QuickAction icon="💹" title="ROI分析" desc="效益分析" onClick={() => onNavigate("roi")} color="pink" />
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color }: { icon: string; label: string; value: number | string; color: string }) {
  const colors: Record<string, { bg: string; border: string; text: string }> = {
    purple: { bg: "bg-purple-500/10", border: "border-purple-500/30", text: "text-purple-400" },
    green: { bg: "bg-green-500/10", border: "border-green-500/30", text: "text-green-400" },
    blue: { bg: "bg-blue-500/10", border: "border-blue-500/30", text: "text-blue-400" },
    yellow: { bg: "bg-yellow-500/10", border: "border-yellow-500/30", text: "text-yellow-400" },
  };
  const c = colors[color] || colors.purple;

  return (
    <div className={`p-5 rounded-xl ${c.bg} border ${c.border}`}>
      <div className="flex items-center gap-4">
        <span className="text-3xl">{icon}</span>
        <div>
          <div className={`text-2xl font-bold ${c.text}`}>{value}</div>
          <div className="text-white/50 text-sm mt-0.5">{label}</div>
        </div>
      </div>
    </div>
  );
}

function QuickAction({ icon, title, desc, onClick, color }: { icon: string; title: string; desc: string; onClick: () => void; color: string }) {
  const colors: Record<string, string> = {
    purple: "hover:border-purple-400/50 hover:bg-purple-500/10",
    cyan: "hover:border-cyan-400/50 hover:bg-cyan-500/10",
    green: "hover:border-green-400/50 hover:bg-green-500/10",
    orange: "hover:border-orange-400/50 hover:bg-orange-500/10",
    pink: "hover:border-pink-400/50 hover:bg-pink-500/10",
  };

  return (
    <button
      onClick={onClick}
      className={`p-5 rounded-xl bg-white/5 border border-white/10 text-left transition-all ${colors[color] || colors.purple}`}
    >
      <div className="text-2xl mb-2">{icon}</div>
      <div className="text-white font-medium">{title}</div>
      <div className="text-white/40 text-sm mt-1">{desc}</div>
    </button>
  );
}

// 副业推荐页面
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
      const data = await res.json();
      setResult(data);
    } catch {
      setError("请求失败，请检查后端服务是否启动");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Hero Form */}
      <div className="relative rounded-2xl overflow-hidden">
        <HeroBackground />
        <div className="relative z-10 p-8" style={{ background: "linear-gradient(135deg, rgba(15,15,40,0.75) 0%, rgba(30,27,75,0.6) 50%, rgba(15,15,40,0.8) 100%)" }}>
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-xl bg-purple-600/40 border border-purple-400/30 flex items-center justify-center">
              <span className="text-2xl">📡</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">开始智能匹配</h2>
              <p className="text-white/50 mt-1">填写信息，多智能体协同分析您的最佳副业方向</p>
            </div>
          </div>
          <UserForm onSubmit={handleSubmit} disabled={loading} />
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="relative rounded-2xl overflow-hidden">
          <HeroBackground />
          <div className="relative z-10 bg-white/[0.05] backdrop-blur-xl border border-white/10 rounded-2xl p-16 text-center">
            <LoadingSpinner />
            <p className="text-white mt-8 text-xl font-medium">深度分析中...</p>
            <p className="text-white/40 mt-2">多智能体协同推理 · 请稍候</p>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6 text-red-400 text-center font-medium">
          {error}
        </div>
      )}

      {/* Results */}
      {result?.success && result.data && (
        <div className="space-y-5">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-green-500/20 border border-green-500/30 flex items-center justify-center">
              <span className="text-2xl">🎯</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">为您推荐</h2>
              <p className="text-white/40 mt-1">基于深度画像分析生成</p>
            </div>
          </div>
          <ResultCard data={result.data} />
        </div>
      )}

      {result && !result.success && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-6 text-yellow-400 text-center font-medium">
          {result.message}
        </div>
      )}
    </div>
  );
}

// 主应用
export default function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [showConfig, setShowConfig] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [showAdmin, setShowAdmin] = useState(false);
  const [currentUser, setCurrentUser] = useState<{ id: number; username: string; role: string } | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    getConfig().then(setConfig).catch(() => {});

    const storedUser = localStorage.getItem("auth_user");
    if (storedUser) {
      try {
        setCurrentUser(JSON.parse(storedUser));
      } catch { }
    }
  }, []);

  const handleLogin = async (_token: string, user: any) => {
    setCurrentUser(user);
    setShowLogin(false);
  };

  const handleLogout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("auth_user");
    setCurrentUser(null);
    setPage("dashboard");
  };

  const handleSaveConfig = async (newConfig: AppConfig) => {
    try {
      await saveConfig(newConfig);
      setConfig(newConfig);
      setShowConfig(false);
    } catch {
      alert("保存配置失败");
    }
  };

  const currentPageInfo = PAGE_INFO[page];

  // 判断是否在子页面
  const isSubPage = page !== "dashboard";

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-950 to-indigo-950 flex">
      {/* 侧边栏 */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-white/[0.03] border-r border-white/[0.08] flex flex-col transition-all duration-300 sticky top-0 h-screen`}>
        {/* Logo */}
        <div className="p-4 border-b border-white/[0.08]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-600/40 border border-purple-400/30 flex items-center justify-center flex-shrink-0">
              <span className="text-xl">📡</span>
            </div>
            {sidebarOpen && (
              <div>
                <h1 className="text-lg font-bold text-white">副业雷达</h1>
                <p className="text-white/30 text-xs">多平台管理</p>
              </div>
            )}
          </div>
        </div>

        {/* 导航列表 */}
        <nav className="flex-1 p-3 overflow-y-auto">
          {WORKFLOW_SECTIONS.map((section) => (
            <div key={section.id} className="mb-4">
              {sidebarOpen && (
                <div className="text-xs font-medium text-white/30 uppercase tracking-wider px-3 mb-2">
                  {section.label}
                </div>
              )}
              <div className="space-y-1">
                {section.items.map((item) => {
                  const info = PAGE_INFO[item as Page];
                  const isActive = page === item;
                  return (
                    <button
                      key={item}
                      onClick={() => setPage(item as Page)}
                      className={`w-full px-3 py-2.5 rounded-lg text-left flex items-center gap-3 transition-all ${
                        isActive
                          ? "bg-purple-600/30 text-purple-200 border border-purple-500/30"
                          : "text-white/50 hover:text-white hover:bg-white/5"
                      }`}
                    >
                      <span className="text-lg flex-shrink-0">{info.icon}</span>
                      {sidebarOpen && (
                        <span className="text-sm font-medium">{info.title}</span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* 折叠按钮 */}
        <div className="p-3 border-t border-white/[0.08]">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-full px-3 py-2 rounded-lg text-white/40 hover:text-white hover:bg-white/5 transition-all flex items-center justify-center gap-2 text-sm"
          >
            <span>{sidebarOpen ? '◀' : '▶'}</span>
            {sidebarOpen && <span>收起</span>}
          </button>
        </div>
      </aside>

      {/* 主内容区 */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* 顶部栏 */}
        <header className="bg-white/[0.03] border-b border-white/[0.08] px-6 py-4 sticky top-0 z-40">
          <div className="flex items-center justify-between">
            <div>
              {/* 面包屑 */}
              <div className="flex items-center gap-2 text-sm text-white/40 mb-1">
                <button onClick={() => setPage("dashboard")} className="hover:text-white transition-colors">工作台</button>
                {isSubPage && (
                  <>
                    <span>›</span>
                    <span className="text-white/60">{currentPageInfo.section === 'analyze' ? '副业分析' : currentPageInfo.section === 'create' ? '内容创作' : currentPageInfo.section === 'publish' ? '发布管理' : currentPageInfo.section === 'data' ? '数据分析' : ''}</span>
                    <span>›</span>
                    <span className="text-white">{currentPageInfo.title}</span>
                  </>
                )}
              </div>
              {/* 页面标题 */}
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <span>{currentPageInfo.icon}</span>
                <span>{currentPageInfo.title}</span>
              </h2>
            </div>

            {/* 用户操作 */}
            <div className="flex items-center gap-3">
              {currentUser ? (
                <>
                  <span className="text-white/60 text-sm">
                    <span className="text-purple-400 font-medium">{currentUser.username}</span>
                  </span>
                  {currentUser.role === "admin" && (
                    <button
                      onClick={() => setShowAdmin(true)}
                      className="px-3 py-1.5 bg-purple-600/30 hover:bg-purple-600/50 text-purple-300 rounded-lg text-sm border border-purple-500/30"
                    >
                      管理
                    </button>
                  )}
                  <button
                    onClick={() => setShowConfig(true)}
                    className="px-3 py-1.5 bg-white/5 hover:bg-white/10 text-white/60 rounded-lg text-sm border border-white/10"
                  >
                    ⚙️ 设置
                  </button>
                  <button
                    onClick={handleLogout}
                    className="px-3 py-1.5 bg-white/5 hover:bg-white/10 text-white/60 rounded-lg text-sm border border-white/10"
                  >
                    退出
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setShowLogin(true)}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium flex items-center gap-2"
                >
                  <span>🔐</span>
                  <span>登录</span>
                </button>
              )}
            </div>
          </div>
        </header>

        {/* 页面描述 */}
        {isSubPage && (
          <div className="px-6 py-3 bg-white/[0.02] border-b border-white/[0.05]">
            <p className="text-sm text-white/50">{currentPageInfo.desc}</p>
          </div>
        )}

        {/* 主内容 */}
        <main className="flex-1 p-6 overflow-y-auto">
          {page === "dashboard" && <Dashboard onNavigate={setPage} />}
          {page === "hustle" && <HustlePage />}
          {page === "content" && (
            <ContentManager token={getToken() || ""} onBack={() => setPage("dashboard")} />
          )}
          {page === "analytics" && (
            <AnalyticsDashboard token={getToken() || ""} onBack={() => setPage("dashboard")} />
          )}
          {page === "platforms" && (
            <PlatformManager token={getToken() || ""} onBack={() => setPage("dashboard")} />
          )}
          {page === "materials" && (
            <MaterialManager token={getToken() || ""} onBack={() => setPage("dashboard")} />
          )}
          {page === "scheduled" && (
            <ScheduledPostsManager token={getToken() || ""} onBack={() => setPage("dashboard")} />
          )}
          {page === "hottopics" && (
            <HotTopicsPanel token={getToken() || ""} onBack={() => setPage("dashboard")} />
          )}
          {page === "check" && (
            <ContentCheckPanel token={getToken() || ""} onBack={() => setPage("dashboard")} />
          )}
          {page === "roi" && (
            <ROIAnalysisPanel token={getToken() || ""} onBack={() => setPage("dashboard")} />
          )}
        </main>
      </div>

      {/* Modals */}
      {showConfig && (
        <ConfigModal config={config} onSave={handleSaveConfig} onClose={() => setShowConfig(false)} />
      )}

      {showLogin && (
        <LoginModal onClose={() => setShowLogin(false)} onLogin={handleLogin} />
      )}

      {showAdmin && (
        <AdminPanel onClose={() => setShowAdmin(false)} />
      )}
    </div>
  );
}
