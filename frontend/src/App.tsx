import { useState, useEffect } from "react";
import { getRecommendation, getConfig, saveConfig, UserInput, RecommendationResult, AppConfig } from "./api";
import UserForm from "./components/UserForm";
import ResultCard from "./components/ResultCard";
import LoadingSpinner from "./components/LoadingSpinner";
import ConfigModal from "./components/ConfigModal";

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RecommendationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [showConfig, setShowConfig] = useState(false);

  useEffect(() => {
    // 加载配置
    getConfig().then(setConfig).catch(() => {});
  }, []);

  const handleSubmit = async (input: UserInput) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await getRecommendation(input);
      setResult(res);
    } catch (err) {
      setError("请求失败，请检查后端服务是否启动");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConfig = async (newConfig: AppConfig) => {
    try {
      await saveConfig(newConfig);
      setConfig(newConfig);
      setShowConfig(false);
    } catch (err) {
      alert("保存配置失败");
    }
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-sm border-b border-white/20">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">副业雷达</h1>
              <p className="text-white/70 mt-1">基于多智能体协同的个性化轻创业推荐系统</p>
            </div>
            <button
              onClick={() => setShowConfig(true)}
              className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors"
            >
              ⚙️ 设置
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Form */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-2xl p-8 sticky top-8">
              <h2 className="text-xl font-semibold text-gray-800 mb-6">填写您的信息</h2>
              <UserForm onSubmit={handleSubmit} disabled={loading} />
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2 space-y-6">
            {/* Loading */}
            {loading && (
              <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
                <LoadingSpinner />
                <p className="text-gray-500 mt-6 text-lg">正在分析您的画像...</p>
                <p className="text-gray-400 text-sm mt-2">这可能需要几秒钟</p>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-red-700 text-center text-lg">
                {error}
              </div>
            )}

            {/* Results */}
            {result?.success && result.data && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-white">为您推荐</h2>
                  <span className="px-4 py-2 bg-green-500/20 text-green-300 rounded-full text-sm">
                    基于 {config?.llm_provider || 'DeepSeek'} 大模型
                  </span>
                </div>
                <ResultCard data={result.data} />
              </div>
            )}

            {result && !result.success && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-6 text-yellow-700 text-center text-lg">
                {result.message}
              </div>
            )}

            {/* Empty State */}
            {!loading && !result && (
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-12 text-center border border-white/20">
                <div className="text-6xl mb-4">🎯</div>
                <h3 className="text-2xl font-bold text-white mb-2">开始您的副业之旅</h3>
                <p className="text-white/70 text-lg">填写左侧表单，获取个性化副业推荐</p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/20 bg-white/5 backdrop-blur-sm mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6 text-center text-white/60">
          副业雷达 v0.1.0 | 支持 DeepSeek / 千问 / Kimi / MiniMax / OpenAI
        </div>
      </footer>

      {/* Config Modal */}
      {showConfig && (
        <ConfigModal
          config={config}
          onSave={handleSaveConfig}
          onClose={() => setShowConfig(false)}
        />
      )}
    </div>
  );
}

export default App;