import { useState, useEffect } from "react";

interface AnalyticsData {
  views: number;
  likes: number;
  comments: number;
  shares: number;
  followers: number;
  revenue: number;
  date: string;
  platform: string;
}

interface Summary {
  totals: {
    total_views: number;
    total_likes: number;
    total_comments: number;
    total_shares: number;
    total_revenue: number;
  };
  platforms: { platform: string; views: number; revenue: number }[];
  trend: { date: string; views: number; revenue: number }[];
}

interface Props {
  token: string;
  onBack: () => void;
}

export default function AnalyticsDashboard({ token, onBack }: Props) {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [platform, setPlatform] = useState("wechat_public");
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]);
  const [formData, setFormData] = useState({
    views: 0,
    likes: 0,
    comments: 0,
    shares: 0,
    followers: 0,
    revenue: 0,
  });

  useEffect(() => {
    fetchData();
  }, [token]);

  const fetchData = async () => {
    try {
      // 获取汇总数据
      const summaryRes = await fetch("/api/analytics/summary", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const summaryData = await summaryRes.json();
      if (summaryData.success) {
        setSummary(summaryData.summary);
      }

      // 获取详细数据
      const analyticsRes = await fetch("/api/analytics?days=30", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const analyticsData = await analyticsRes.json();
      if (analyticsData.success) {
        setAnalytics(analyticsData.analytics || []);
      }
    } catch (error) {
      console.error("获取分析数据失败:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("/api/analytics", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          platform,
          date,
          ...formData,
        }),
      });
      const data = await res.json();
      if (data.success) {
        setShowAddForm(false);
        fetchData();
        setFormData({ views: 0, likes: 0, comments: 0, shares: 0, followers: 0, revenue: 0 });
      }
    } catch (error) {
      console.error("提交失败:", error);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 10000) return (num / 10000).toFixed(1) + "万";
    if (num >= 1000) return (num / 1000).toFixed(1) + "k";
    return num.toString();
  };

  const platformNames: Record<string, string> = {
    wechat_public: "公众号",
    toutiao: "头条号",
    xiaohongshu: "小红书",
    zhihu: "知乎",
    douyin: "抖音",
    bsite: "B站",
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/60">加载中...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">数据分析</h1>
          <p className="text-white/50 text-sm mt-1">跟踪您的内容表现和收益</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-sm font-medium transition-colors"
          >
            {showAddForm ? "取消录入" : "录入数据"}
          </button>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-medium transition-colors"
          >
            返回
          </button>
        </div>
      </div>

      {/* Add Data Form */}
      {showAddForm && (
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
          <h3 className="text-lg font-medium text-white mb-4">录入数据</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-white/60 text-sm mb-1">平台</label>
                <select
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value)}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white"
                >
                  <option value="wechat_public">公众号</option>
                  <option value="toutiao">头条号</option>
                  <option value="xiaohongshu">小红书</option>
                  <option value="zhihu">知乎</option>
                  <option value="douyin">抖音</option>
                  <option value="bsite">B站</option>
                </select>
              </div>
              <div>
                <label className="block text-white/60 text-sm mb-1">日期</label>
                <input
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white"
                />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-white/60 text-sm mb-1">阅读量</label>
                <input
                  type="number"
                  value={formData.views}
                  onChange={(e) => setFormData({ ...formData, views: Number(e.target.value) })}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white"
                />
              </div>
              <div>
                <label className="block text-white/60 text-sm mb-1">点赞数</label>
                <input
                  type="number"
                  value={formData.likes}
                  onChange={(e) => setFormData({ ...formData, likes: Number(e.target.value) })}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white"
                />
              </div>
              <div>
                <label className="block text-white/60 text-sm mb-1">评论数</label>
                <input
                  type="number"
                  value={formData.comments}
                  onChange={(e) => setFormData({ ...formData, comments: Number(e.target.value) })}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white"
                />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-white/60 text-sm mb-1">粉丝数</label>
                <input
                  type="number"
                  value={formData.followers}
                  onChange={(e) => setFormData({ ...formData, followers: Number(e.target.value) })}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white"
                />
              </div>
              <div>
                <label className="block text-white/60 text-sm mb-1">收益 (元)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.revenue}
                  onChange={(e) => setFormData({ ...formData, revenue: Number(e.target.value) })}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white"
                />
              </div>
              <div>
                <label className="block text-white/60 text-sm mb-1">分享数</label>
                <input
                  type="number"
                  value={formData.shares}
                  onChange={(e) => setFormData({ ...formData, shares: Number(e.target.value) })}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white"
                />
              </div>
            </div>
            <button
              type="submit"
              className="w-full py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all"
            >
              提交数据
            </button>
          </form>
        </div>
      )}

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/10 rounded-2xl p-5 border border-purple-500/20">
            <div className="text-white/60 text-sm">总阅读量</div>
            <div className="text-3xl font-bold text-white mt-1">{formatNumber(summary.totals.total_views)}</div>
          </div>
          <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/10 rounded-2xl p-5 border border-blue-500/20">
            <div className="text-white/60 text-sm">总收益</div>
            <div className="text-3xl font-bold text-white mt-1">¥{summary.totals.total_revenue.toFixed(2)}</div>
          </div>
          <div className="bg-gradient-to-br from-pink-500/20 to-pink-600/10 rounded-2xl p-5 border border-pink-500/20">
            <div className="text-white/60 text-sm">总点赞</div>
            <div className="text-3xl font-bold text-white mt-1">{formatNumber(summary.totals.total_likes)}</div>
          </div>
          <div className="bg-gradient-to-br from-green-500/20 to-green-600/10 rounded-2xl p-5 border border-green-500/20">
            <div className="text-white/60 text-sm">总评论</div>
            <div className="text-3xl font-bold text-white mt-1">{formatNumber(summary.totals.total_comments)}</div>
          </div>
        </div>
      )}

      {/* Platform Breakdown */}
      {summary && summary.platforms.length > 0 && (
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
          <h3 className="text-lg font-medium text-white mb-4">平台分布</h3>
          <div className="space-y-3">
            {summary.platforms.map((p) => (
              <div key={p.platform} className="flex items-center justify-between">
                <span className="text-white/80">{platformNames[p.platform] || p.platform}</span>
                <div className="flex items-center gap-4">
                  <span className="text-white/60 text-sm">{formatNumber(p.views)} 阅读</span>
                  <span className="text-green-400 text-sm">¥{p.revenue.toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Trend Chart (Simple) */}
      {summary && summary.trend.length > 0 && (
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
          <h3 className="text-lg font-medium text-white mb-4">近7天趋势</h3>
          <div className="flex items-end gap-2 h-32">
            {summary.trend.map((t, i) => {
              const maxViews = Math.max(...summary.trend.map((x) => x.views), 1);
              const height = (t.views / maxViews) * 100;
              return (
                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                  <div
                    className="w-full bg-gradient-to-t from-purple-600 to-purple-400 rounded-t-md transition-all"
                    style={{ height: `${height}%`, minHeight: t.views > 0 ? "4px" : "0" }}
                  />
                  <span className="text-white/40 text-xs">{t.date.slice(5)}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Recent Records */}
      <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
        <h3 className="text-lg font-medium text-white mb-4">最近记录</h3>
        {analytics.length === 0 ? (
          <div className="text-white/40 text-center py-8">暂无数据，开始录入您的第一份数据吧</div>
        ) : (
          <div className="space-y-3">
            {analytics.slice(0, 10).map((a, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                <div className="flex items-center gap-3">
                  <span className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded text-xs">
                    {platformNames[a.platform] || a.platform}
                  </span>
                  <span className="text-white/60 text-sm">{a.date}</span>
                </div>
                <div className="flex items-center gap-6 text-sm">
                  <span className="text-white/80">{formatNumber(a.views)}</span>
                  <span className="text-pink-400">❤️ {formatNumber(a.likes)}</span>
                  <span className="text-green-400">¥{a.revenue.toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
