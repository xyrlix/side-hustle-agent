import { useState } from "react";
import { checkContent, ContentViolation } from "../api";

interface Props {
  token?: string;
  onBack: () => void;
  initialTitle?: string;
  initialBody?: string;
}

export default function ContentCheckPanel({ onBack, initialTitle = "", initialBody = "" }: Props) {
  const [title, setTitle] = useState(initialTitle);
  const [body, setBody] = useState(initialBody);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleCheck = async () => {
    if (!title.trim() && !body.trim()) {
      alert("请输入标题或内容");
      return;
    }

    setLoading(true);
    try {
      const res = await checkContent(title, body);
      setResult(res);
    } catch (e) {
      console.error("检测失败:", e);
    } finally {
      setLoading(false);
    }
  };

  const getViolationTypeIcon = (type: string) => {
    switch (type) {
      case "ad": return "🚫";
      case "limit": return "⚠️";
      case "quality": return "📝";
      default: return "❌";
    }
  };

  const getViolationTypeColor = (type: string) => {
    switch (type) {
      case "ad": return "text-red-400 bg-red-500/10 border-red-500/30";
      case "limit": return "text-yellow-400 bg-yellow-500/10 border-yellow-500/30";
      case "quality": return "text-blue-400 bg-blue-500/10 border-blue-500/30";
      default: return "text-white/60 bg-white/5 border-white/10";
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">内容违规检测</h1>
          <p className="text-white/50 text-sm mt-1">检测违规词、广告词、平台限流风险</p>
        </div>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-medium transition-colors"
        >
          返回
        </button>
      </div>

      {/* Input Form */}
      <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6 space-y-4">
        <div>
          <label className="block text-white/60 text-sm mb-2">标题</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="输入内容标题..."
            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-purple-500/50"
          />
        </div>
        <div>
          <label className="block text-white/60 text-sm mb-2">正文内容</label>
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="输入内容正文..."
            rows={10}
            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-purple-500/50 resize-none"
          />
        </div>
        <button
          onClick={handleCheck}
          disabled={loading}
          className="w-full py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-600/50 text-white rounded-xl font-medium transition-colors flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>检测中...</span>
            </>
          ) : (
            <>
              <span>🔍</span>
              <span>开始检测</span>
            </>
          )}
        </button>
      </div>

      {/* Result */}
      {result && (
        <div className="space-y-4">
          {/* Summary Card */}
          <div className={`rounded-2xl p-6 border ${
            result.passed
              ? "bg-green-500/10 border-green-500/30"
              : "bg-red-500/10 border-red-500/30"
          }`}>
            <div className="flex items-center gap-4">
              <div className={`w-16 h-16 rounded-2xl flex items-center justify-center text-3xl ${
                result.passed ? "bg-green-500/20" : "bg-red-500/20"
              }`}>
                {result.passed ? "✅" : "❌"}
              </div>
              <div className="flex-1">
                <div className={`text-2xl font-bold ${
                  result.passed ? "text-green-400" : "text-red-400"
                }`}>
                  {result.passed ? "检测通过" : "检测未通过"}
                </div>
                <div className="text-white/60 mt-1">{result.summary}</div>
              </div>
              <div className="text-center">
                <div className={`text-4xl font-bold ${
                  result.score >= 80 ? "text-green-400" :
                  result.score >= 60 ? "text-yellow-400" :
                  "text-red-400"
                }`}>
                  {result.score}
                </div>
                <div className="text-white/40 text-sm">内容分</div>
              </div>
            </div>
          </div>

          {/* Violations */}
          {result.violations && result.violations.length > 0 && (
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-bold text-white mb-4">
                违规详情 ({result.violations.length} 处)
              </h3>
              <div className="space-y-3">
                {result.violations.map((v: ContentViolation, index: number) => (
                  <div
                    key={index}
                    className={`p-4 rounded-xl border ${getViolationTypeColor(v.type)}`}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-xl">{getViolationTypeIcon(v.type)}</span>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium">{v.category}</span>
                          <span className="text-xs px-2 py-0.5 bg-white/10 rounded">
                            {v.type === "ad" ? "广告违规" :
                             v.type === "limit" ? "限流风险" : "质量问题"}
                          </span>
                        </div>
                        <div className="text-sm">
                          关键词: <code className="px-1 py-0.5 bg-white/10 rounded">{v.word}</code>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Suggestions */}
          {result.suggestions && result.suggestions.length > 0 && (
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
              <h3 className="text-lg font-bold text-white mb-4">修改建议</h3>
              <div className="space-y-3">
                {result.suggestions.map((s: any, index: number) => (
                  <div
                    key={index}
                    className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30"
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-xl">💡</span>
                      <div className="flex-1">
                        <div className="text-blue-300 font-medium mb-1">
                          {s.original}
                        </div>
                        <div className="text-white/80 text-sm">
                          建议: {s.suggestion}
                        </div>
                        <div className="text-white/50 text-xs mt-1">
                          原因: {s.reason}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Stats */}
          {(result.ad_violations_count > 0 || result.limit_violations_count > 0) && (
            <div className="grid grid-cols-2 gap-4">
              {result.ad_violations_count > 0 && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-5 text-center">
                  <div className="text-3xl font-bold text-red-400">{result.ad_violations_count}</div>
                  <div className="text-white/60 text-sm mt-1">广告违规词</div>
                </div>
              )}
              {result.limit_violations_count > 0 && (
                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-2xl p-5 text-center">
                  <div className="text-3xl font-bold text-yellow-400">{result.limit_violations_count}</div>
                  <div className="text-white/60 text-sm mt-1">限流风险词</div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
