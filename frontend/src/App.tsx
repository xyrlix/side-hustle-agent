import { useState, useEffect } from "react";
import { getConfig, saveConfig, UserInput, RecommendationResult, AppConfig, getAnalyticsSummary } from "./api";
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

type Page = "dashboard" | "hustle" | "content" | "analytics" | "platforms" | "materials";

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
    <div className="space-y-8">
      {/* 欢迎区块 */}
      <div className="relative rounded-3xl overflow-hidden">
        <HeroBackground />
        <div className="relative z-10 p-10 bg-gradient-to-r from-purple-900/60 to-indigo-900/60 backdrop-blur-sm border border-white/10 rounded-3xl">
          <h2 className="text-4xl font-bold text-white mb-3">欢迎使用副业雷达</h2>
          <p className="text-white/60 text-lg">基于 AI 智能分析，为你匹配最适合的副业方向</p>
          <div className="flex gap-4 mt-8">
            <button
              onClick={() => onNavigate("hustle")}
              className="px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium text-lg flex items-center gap-3 transition-all shadow-lg shadow-purple-500/30"
            >
              <span className="text-2xl">🎯</span> 开始副业推荐
            </button>
            <button
              onClick={() => onNavigate("content")}
              className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white rounded-xl font-medium text-lg flex items-center gap-3 transition-all border border-white/20"
            >
              <span className="text-2xl">📝</span> 内容管理
            </button>
          </div>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-4 gap-6">
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
      <div className="grid grid-cols-4 gap-6">
        <QuickAction
          icon="🤖"
          title="AI 内容生成"
          desc="使用 AI 快速生成各平台适配内容"
          onClick={() => onNavigate("content")}
          color="cyan"
        />
        <QuickAction
          icon="📰"
          title="副业推荐分析"
          desc="智能匹配最适合你的副业方向"
          onClick={() => onNavigate("hustle")}
          color="purple"
        />
        <QuickAction
          icon="📈"
          title="数据看板"
          desc="查看内容运营数据和收益分析"
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
    <div className={`p-6 rounded-2xl ${c.bg} border ${c.border}`}>
      <div className="flex items-center gap-4">
        <span className="text-3xl">{icon}</span>
        <div>
          <div className={`text-3xl font-bold ${c.text}`}>{value}</div>
          <div className="text-white/40 text-sm">{label}</div>
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
  };
  const c = colors[color] || colors.purple;

  return (
    <button
      onClick={onClick}
      className={`p-8 rounded-2xl ${c.bg} ${c.hover} border ${c.border} text-left transition-all group`}
    >
      <div className="text-4xl mb-4">{icon}</div>
      <div className="text-white font-bold text-xl mb-2 group-hover:text-purple-300 transition-colors">{title}</div>
      <div className="text-white/50">{desc}</div>
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
    <div className="space-y-8">
      {/* Hero Form */}
      <div className="relative rounded-3xl overflow-hidden">
        <HeroBackground />
        <div
          className="relative z-10 p-10"
          style={{
            background: "linear-gradient(135deg, rgba(15,15,40,0.75) 0%, rgba(30,27,75,0.6) 50%, rgba(15,15,40,0.8) 100%)",
          }}
        >
          <div className="flex items-center gap-4 mb-6">
            <div className="w-12 h-12 rounded-2xl bg-purple-600/40 border border-purple-400/30 flex items-center justify-center backdrop-blur-sm">
              <span className="text-2xl">📡</span>
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white">开始智能匹配</h2>
              <p className="text-white/50 text-base mt-0.5">填写信息，多智能体协同分析您的最佳副业方向</p>
            </div>
          </div>
          <UserForm onSubmit={handleSubmit} disabled={loading} />
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="relative rounded-3xl overflow-hidden">
          <HeroBackground />
          <div className="relative z-10 bg-white/[0.05] backdrop-blur-xl border border-white/10 rounded-3xl p-20 text-center">
            <LoadingSpinner />
            <p className="text-white mt-12 text-2xl font-medium tracking-wide">深度分析中...</p>
            <p className="text-white/40 mt-3 text-base">多智能体协同推理 · 请稍候</p>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-500/10 border-2 border-red-500/30 rounded-3xl p-10 text-red-400 text-xl text-center font-medium">
          {error}
        </div>
      )}

      {/* Results */}
      {result?.success && result.data && (
        <div className="space-y-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-green-500/20 border border-green-500/30 flex items-center justify-center">
              <span className="text-3xl">🎯</span>
            </div>
            <div>
              <h2 className="text-4xl font-bold text-white">为您推荐</h2>
              <p className="text-white/40 mt-1 text-sm">基于深度画像分析生成</p>
            </div>
          </div>
          <ResultCard data={result.data} />
        </div>
      )}

      {result && !result.success && (
        <div className="bg-yellow-500/10 border-2 border-yellow-500/30 rounded-3xl p-10 text-yellow-400 text-xl text-center font-medium">
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

  const navItems: { id: Page; label: string; icon: string }[] = [
    { id: "dashboard", label: "仪表板", icon: "📊" },
    { id: "hustle", label: "副业推荐", icon: "🎯" },
    { id: "content", label: "内容管理", icon: "📝" },
    { id: "analytics", label: "数据分析", icon: "📈" },
    { id: "platforms", label: "平台管理", icon: "🔗" },
    { id: "materials", label: "素材库", icon: "📦" },
  ];

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
        <div className="max-w-7xl mx-auto px-8 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-purple-600/40 border border-purple-400/30 flex items-center justify-center">
                <span className="text-xl">📡</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">副业雷达</h1>
                <p className="text-white/30 text-xs">多平台社交媒体管理</p>
              </div>
            </div>

            {/* Navigation */}
            <nav className="flex items-center gap-2">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setPage(item.id)}
                  className={`px-5 py-2.5 rounded-xl text-sm font-medium flex items-center gap-2 transition-all ${
                    page === item.id
                      ? "bg-purple-600/40 text-purple-200 border border-purple-400/40"
                      : "text-white/50 hover:text-white hover:bg-white/5"
                  }`}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </button>
              ))}
            </nav>

            {/* User Actions */}
            <div className="flex items-center gap-3">
              {currentUser ? (
                <>
                  <div className="text-white/60 text-sm">
                    <span className="text-purple-400 font-medium">{currentUser.username}</span>
                  </div>
                  {currentUser.role === "admin" && (
                    <button
                      onClick={() => setShowAdmin(true)}
                      className="px-4 py-2 bg-purple-600/30 hover:bg-purple-600/50 text-purple-300 rounded-xl text-sm border border-purple-500/30"
                    >
                      管理
                    </button>
                  )}
                  <button
                    onClick={() => setShowConfig(true)}
                    className="px-4 py-2 bg-white/8 hover:bg-white/12 text-white/70 rounded-xl text-sm border border-white/10"
                  >
                    设置
                  </button>
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 bg-white/8 hover:bg-white/12 text-white/70 rounded-xl text-sm border border-white/10"
                  >
                    退出
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setShowLogin(true)}
                  className="px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-sm font-medium flex items-center gap-2"
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
      <main className="relative z-10 max-w-7xl mx-auto px-8 py-10">
        {page === "dashboard" && <Dashboard onNavigate={setPage} />}
        {page === "hustle" && <HustlePage />}
        {page === "content" && (
          <ContentManager token={token} onBack={() => setPage("dashboard")} />
        )}
        {page === "analytics" && (
          <AnalyticsDashboard token={token} onBack={() => setPage("dashboard")} />
        )}
        {page === "platforms" && (
          <PlatformManager token={token} onBack={() => setPage("dashboard")} />
        )}
        {page === "materials" && (
          <MaterialManager token={token} onBack={() => setPage("dashboard")} />
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