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
    <div className="space-y-5">
      {/* 欢迎区块 */}
      <div className="relative rounded-2xl overflow-hidden">
        <HeroBackground />
        <div className="relative z-10 p-6 bg-gradient-to-r from-purple-900/60 to-indigo-900/60 backdrop-blur-sm border border-white/10 rounded-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-white">欢迎使用副业雷达</h2>
              <p className="text-white/50 text-sm mt-1">基于 AI 智能分析，为你匹配最适合的副业方向</p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => onNavigate("hustle")}
                className="px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium flex items-center gap-2 transition-all"
              >
                <span>🎯</span> 副业推荐
              </button>
              <button
                onClick={() => onNavigate("content")}
                className="px-5 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-lg font-medium flex items-center gap-2 transition-all border border-white/20"
              >
                <span>📝</span> 内容管理
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard
          icon="📊"
          label="内容总数"
          value={stats?.total_content || 0}
          color="purple"
        />
        <StatCard
          icon="✅"
          label="已发布"
          value={stats?.published || 0}
          color="green"
        />
        <StatCard
          icon="👁️"
          label="总阅读量"
          value={stats?.total_views || 0}
          color="blue"
        />
        <StatCard
          icon="💰"
          label="总收益"
          value={`¥${stats?.total_revenue || 0}`}
          color="yellow"
        />
      </div>

      {/* 快捷操作 */}
      <div className="grid grid-cols-4 gap-4">
        <QuickAction
          icon="🤖"
          title="AI 内容生成"
          desc="快速生成各平台适配内容"
          onClick={() => onNavigate("content")}
          color="cyan"
        />
        <QuickAction
          icon="📰"
          title="副业推荐分析"
          desc="智能匹配最适合你的副业"
          onClick={() => onNavigate("hustle")}
          color="purple"
        />
        <QuickAction
          icon="📈"
          title="数据看板"
          desc="查看运营数据和收益分析"
          onClick={() => onNavigate("analytics")}
          color="green"
        />
        <QuickAction
          icon="📦"
          title="平台管理"
          desc="管理社交媒体平台账号"
          onClick={() => onNavigate("platforms")}
          color="orange"
        />
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
    <div className={`p-4 rounded-xl ${c.bg} border ${c.border}`}>
      <div className="flex items-center gap-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <div className={`text-2xl font-bold ${c.text}`}>{value}</div>
          <div className="text-white/40 text-xs">{label}</div>
        </div>
      </div>
    </div>
  );
}

function QuickAction({ icon, title, desc, onClick, color }: { icon: string; title: string; desc: string; onClick: () => void; color: string }) {
  const colors: Record<string, { bg: string; hover: string; border: string }> = {
    cyan: { bg: "bg-cyan-500/10", hover: "hover:bg-cyan-500/20", border: "border-cyan-500/30" },
    purple: { bg: "bg-purple-500/10", hover: "hover:bg-purple-500/20", border: "border-purple-500/30" },
    green: { bg: "bg-green-500/10", hover: "hover:bg-green-500/20", border: "border-green-500/30" },
    orange: { bg: "bg-orange-500/10", hover: "hover:bg-orange-500/20", border: "border-orange-500/30" },
  };
  const c = colors[color] || colors.purple;

  return (
    <button
      onClick={onClick}
      className={`p-5 rounded-xl ${c.bg} ${c.hover} border ${c.border} text-left transition-all group`}
    >
      <div className="text-2xl mb-2">{icon}</div>
      <div className="text-white font-bold text-sm mb-1 group-hover:text-purple-300 transition-colors">{title}</div>
      <div className="text-white/40 text-xs">{desc}</div>
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
    <div className="space-y-5">
      {/* Hero Form */}
      <div className="relative rounded-2xl overflow-hidden">
        <HeroBackground />
        <div
          className="relative z-10 p-6"
          style={{
            background: "linear-gradient(135deg, rgba(15,15,40,0.75) 0%, rgba(30,27,75,0.6) 50%, rgba(15,15,40,0.8) 100%)",
          }}
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-purple-600/40 border border-purple-400/30 flex items-center justify-center backdrop-blur-sm">
              <span className="text-xl">📡</span>
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">开始智能匹配</h2>
              <p className="text-white/50 text-sm">填写信息，多智能体协同分析您的最佳副业方向</p>
            </div>
          </div>
          <UserForm onSubmit={handleSubmit} disabled={loading} />
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="relative rounded-2xl overflow-hidden">
          <HeroBackground />
          <div className="relative z-10 bg-white/[0.05] backdrop-blur-xl border border-white/10 rounded-2xl p-12 text-center">
            <LoadingSpinner />
            <p className="text-white mt-6 text-lg font-medium">深度分析中...</p>
            <p className="text-white/40 mt-2 text-sm">多智能体协同推理 · 请稍候</p>
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
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-green-500/20 border border-green-500/30 flex items-center justify-center">
              <span className="text-xl">🎯</span>
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">为您推荐</h2>
              <p className="text-white/40 text-xs">基于深度画像分析生成</p>
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

  // 主导航
  const mainNavItems: { id: Page; label: string; icon: string }[] = [
    { id: "dashboard", label: "首页", icon: "📊" },
    { id: "hustle", label: "副业推荐", icon: "🎯" },
    { id: "content", label: "内容管理", icon: "📝" },
  ];

  // 运营工具
  const toolsNavItems: { id: Page; label: string; icon: string }[] = [
    { id: "analytics", label: "数据分析", icon: "📈" },
    { id: "platforms", label: "平台管理", icon: "🔗" },
    { id: "materials", label: "素材库", icon: "📦" },
    { id: "scheduled", label: "定时发布", icon: "⏰" },
    { id: "hottopics", label: "热点话题", icon: "🔥" },
    { id: "check", label: "内容检测", icon: "🔍" },
    { id: "roi", label: "ROI分析", icon: "💹" },
  ];

  const [showTools, setShowTools] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-950 to-indigo-950">
      {/* Ambient background */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute w-[700px] h-[700px] rounded-full"
          style={{ background: "radial-gradient(circle, rgba(109,40,217,0.3) 0%, transparent 70%)", top: "-15%", left: "-10%", filter: "blur(60px)" }} />
        <div className="absolute w-[500px] h-[500px] rounded-full"
          style={{ background: "radial-gradient(circle, rgba(168,85,247,0.2) 0%, transparent 70%)", top: "20%", right: "-5%", filter: "blur(80px)" }} />
        <div className="absolute w-[400px] h-[400px] rounded-full"
          style={{ background: "radial-gradient(circle, rgba(79,70,229,0.2) 0%, transparent 70%)", bottom: "5%", left: "20%", filter: "blur(80px)" }} />
      </div>

      {/* Header */}
      <header className="relative z-50 bg-white/[0.04] backdrop-blur-xl border-b border-white/[0.08] sticky top-0">
        <div className="max-w-7xl mx-auto px-6 py-3">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-purple-600/40 border border-purple-400/30 flex items-center justify-center">
                <span className="text-lg">📡</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">副业雷达</h1>
              </div>
            </div>

            {/* Navigation */}
            <nav className="flex items-center gap-1">
              {mainNavItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setPage(item.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all ${
                    page === item.id
                      ? "bg-purple-600/40 text-purple-200 border border-purple-400/40"
                      : "text-white/50 hover:text-white hover:bg-white/5"
                  }`}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </button>
              ))}

              {/* 运营工具下拉 */}
              <div className="relative">
                <button
                  onClick={() => setShowTools(!showTools)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all ${
                    toolsNavItems.some(item => page === item.id)
                      ? "bg-purple-600/40 text-purple-200 border border-purple-400/40"
                      : "text-white/50 hover:text-white hover:bg-white/5"
                  }`}
                >
                  <span>🛠️</span>
                  <span>运营工具</span>
                  <span className={`text-xs transition-transform ${showTools ? 'rotate-180' : ''}`}>▼</span>
                </button>

                {/* 下拉菜单 */}
                {showTools && (
                  <div className="absolute top-full left-0 mt-2 w-48 bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl py-2 z-50">
                    {toolsNavItems.map((item) => (
                      <button
                        key={item.id}
                        onClick={() => {
                          setPage(item.id);
                          setShowTools(false);
                        }}
                        className={`w-full px-4 py-2.5 text-left text-sm flex items-center gap-3 transition-all ${
                          page === item.id
                            ? "bg-purple-600/30 text-purple-200"
                            : "text-white/60 hover:text-white hover:bg-white/5"
                        }`}
                      >
                        <span>{item.icon}</span>
                        <span>{item.label}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </nav>

            {/* User Actions */}
            <div className="flex items-center gap-2">
              {currentUser ? (
                <>
                  <span className="text-white/40 text-sm">{currentUser.username}</span>
                  {currentUser.role === "admin" && (
                    <button
                      onClick={() => setShowAdmin(true)}
                      className="px-3 py-1.5 bg-purple-600/30 hover:bg-purple-600/50 text-purple-300 rounded-lg text-xs border border-purple-500/30"
                    >
                      管理
                    </button>
                  )}
                  <button
                    onClick={() => setShowConfig(true)}
                    className="px-3 py-1.5 bg-white/5 hover:bg-white/10 text-white/60 rounded-lg text-xs border border-white/10"
                  >
                    ⚙️
                  </button>
                  <button
                    onClick={handleLogout}
                    className="px-3 py-1.5 bg-white/5 hover:bg-white/10 text-white/60 rounded-lg text-xs border border-white/10"
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
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-6">
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