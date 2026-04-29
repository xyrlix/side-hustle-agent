import { useState } from "react";
import { getRecommendation, UserInput, RecommendationResult } from "./api";
import UserForm from "./components/UserForm";
import ResultCard from "./components/ResultCard";
import LoadingSpinner from "./components/LoadingSpinner";

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RecommendationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-5xl font-bold text-white mb-3">副业雷达</h1>
          <p className="text-xl text-white/80">基于多智能体协同的个性化轻创业推荐系统</p>
        </div>

        {/* Main Content */}
        <div className="space-y-6">
          {/* Input Form */}
          <div className="bg-white rounded-2xl shadow-2xl p-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">填写您的信息</h2>
            <UserForm onSubmit={handleSubmit} disabled={loading} />
          </div>

          {/* Loading */}
          {loading && (
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <LoadingSpinner />
              <p className="text-center text-gray-500 mt-4">正在分析您的画像...</p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-center">
              {error}
            </div>
          )}

          {/* Results */}
          {result?.success && result.data && (
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold text-white text-center">为您推荐</h2>
              <ResultCard data={result.data} />
            </div>
          )}

          {result && !result.success && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-yellow-700 text-center">
              {result.message}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-white/60 text-sm">
          副业雷达 v0.1.0 | 基于 DeepSeek / 千问 / Kimi 大模型
        </div>
      </div>
    </div>
  );
}

export default App;