import { useState, useEffect } from "react";
import { getCampaignROI, getContentROI, getROIAdvice, ContentROI, CampaignROI } from "../api";

interface Props {
  token: string;
  onBack: () => void;
}

export default function ROIAnalysisPanel({ token, onBack }: Props) {
  const [campaignROI, setCampaignROI] = useState<CampaignROI | null>(null);
  const [advice, setAdvice] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [targetROI, setTargetROI] = useState(50);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // 加载整体 ROI
      const roiRes = await getCampaignROI();
      if (roiRes.success) {
        setCampaignROI(roiRes.roi);
      }

      // 加载 ROI 建议
      const adviceRes = await getROIAdvice(roiRes.roi?.roi || 0, targetROI);
      if (adviceRes.success) {
        setAdvice(adviceRes.advice);
      }
    } catch (e) {
      console.error("加载失败:", e);
    } finally {
      setLoading(false);
    }
  };

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case "S": return "text-purple-400 bg-purple-500/20";
      case "A": return "text-green-400 bg-green-500/20";
      case "B": return "text-blue-400 bg-blue-500/20";
      case "C": return "text-yellow-400 bg-yellow-500/20";
      case "D": return "text-red-400 bg-red-500/20";
      default: return "text-white/60 bg-white/10";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "good": return "text-green-400 bg-green-500/20";
      case "improve": return "text-yellow-400 bg-yellow-500/20";
      case "review": return "text-red-400 bg-red-500/20";
      default: return "text-white/60 bg-white/10";
    }
  };

  const formatNumber = (num: number | undefined) => {
    if (num === undefined || num === null) return "0";
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toLocaleString();
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">ROI 分析</h1>
          <p className="text-white/50 text-sm mt-1">投资回报率分析，评估内容效益</p>
        </div>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-medium transition-colors"
        >
          返回
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center h-64">
          <div className="text-white/60">加载中...</div>
        </div>
      )}

      {/* Content */}
      {!loading && campaignROI && (
        <div className="space-y-6">
          {/* Overview Stats */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
              <div className="text-white/60 text-sm">总内容数</div>
              <div className="text-3xl font-bold text-white mt-1">{campaignROI.total_content}</div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
              <div className="text-white/60 text-sm">总阅读量</div>
              <div className="text-3xl font-bold text-blue-400 mt-1">{formatNumber(campaignROI.total_views)}</div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
              <div className="text-white/60 text-sm">总收入</div>
              <div className="text-3xl font-bold text-green-400 mt-1">¥{formatNumber(campaignROI.total_revenue)}</div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
              <div className="text-white/60 text-sm">ROI</div>
              <div className={`text-3xl font-bold mt-1 ${
                campaignROI.roi >= 0 ? "text-green-400" : "text-red-400"
              }`}>
                {campaignROI.roi === Infinity ? "∞" : `${campaignROI.roi}%`}
              </div>
            </div>
          </div>

          {/* Secondary Stats */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 text-center">
              <div className="text-white/60 text-sm">平均 CPM</div>
              <div className="text-2xl font-bold text-purple-400 mt-1">¥{campaignROI.avg_cpm}</div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 text-center">
              <div className="text-white/60 text-sm">平均互动率</div>
              <div className="text-2xl font-bold text-cyan-400 mt-1">{campaignROI.avg_engagement}%</div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 text-center">
              <div className="text-white/60 text-sm">总成本</div>
              <div className="text-2xl font-bold text-orange-400 mt-1">¥{formatNumber(campaignROI.total_cost)}</div>
            </div>
          </div>

          {/* Top Content */}
          {campaignROI.top_content && campaignROI.top_content.id && (
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">最佳表现内容</h3>
              <div className="flex items-center gap-4 p-4 bg-green-500/10 border border-green-500/30 rounded-xl">
                <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center text-2xl">
                  🏆
                </div>
                <div className="flex-1">
                  <div className="text-white font-medium">{campaignROI.top_content.title || `内容 #${campaignROI.top_content.id}`}</div>
                  <div className="text-white/60 text-sm mt-1">{formatNumber(campaignROI.top_content.views)} 阅读</div>
                </div>
              </div>
            </div>
          )}

          {/* Platform Breakdown */}
          {campaignROI.platform_breakdown && campaignROI.platform_breakdown.length > 0 && (
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">平台效率排名</h3>
              <div className="space-y-3">
                {campaignROI.platform_breakdown.map((p: any, index: number) => (
                  <div key={p.platform} className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold ${
                      index === 0 ? "bg-yellow-500/20 text-yellow-400" :
                      index === 1 ? "bg-gray-400/20 text-gray-400" :
                      index === 2 ? "bg-orange-500/20 text-orange-400" :
                      "bg-white/10 text-white/60"
                    }`}>
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="text-white font-medium">
                        {p.platform === "wechat_public" ? "公众号" :
                         p.platform === "toutiao" ? "头条号" :
                         p.platform === "xiaohongshu" ? "小红书" :
                         p.platform === "zhihu" ? "知乎" :
                         p.platform === "baijiahao" ? "百家号" :
                         p.platform === "bilibili" ? "B站" :
                         p.platform}
                      </div>
                      <div className="text-white/50 text-sm mt-1">
                        {p.count} 篇 · {formatNumber(p.views)} 阅读 · ¥{formatNumber(p.revenue)} 收益
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-green-400">¥{p.cpm}</div>
                      <div className="text-white/40 text-xs">CPM</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ROI Advice */}
          {advice && (
            <div className={`rounded-2xl p-6 border ${getStatusColor(advice.status)}`}>
              <div className="flex items-start gap-4">
                <div className="text-3xl">
                  {advice.status === "good" ? "🎉" :
                   advice.status === "improve" ? "📈" : "📊"}
                </div>
                <div className="flex-1">
                  <div className="font-bold text-lg mb-2">{advice.message}</div>
                  <div className="space-y-2">
                    {advice.suggestions?.map((s: string, i: number) => (
                      <div key={i} className="flex items-start gap-2 text-sm">
                        <span className="text-white/60">•</span>
                        <span className="text-white/80">{s}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!loading && !campaignROI && (
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-12 border border-white/10 text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-medium text-white mb-2">暂无数据</h3>
          <p className="text-white/50 mb-6">发布内容后即可查看 ROI 分析</p>
          <button
            onClick={onBack}
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium transition-colors"
          >
            返回
          </button>
        </div>
      )}
    </div>
  );
}
