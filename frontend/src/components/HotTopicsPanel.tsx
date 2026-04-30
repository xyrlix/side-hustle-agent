import { useState, useEffect } from "react";
import { getHotTopics, getHotTopicsSources, HotTopic } from "../api";

interface Props {
  token?: string;
  onBack: () => void;
  onSelectTopic?: (topic: string) => void;
}

interface Source {
  id: string;
  name: string;
  icon: string;
}

export default function HotTopicsPanel({ onBack, onSelectTopic }: Props) {
  const [topics, setTopics] = useState<HotTopic[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSources();
    loadTopics();
  }, [selectedSource]);

  const loadSources = async () => {
    try {
      const res = await getHotTopicsSources();
      if (res.success) {
        setSources(res.sources || []);
      }
    } catch (e) {
      console.error("加载来源失败:", e);
    }
  };

  const loadTopics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = selectedSource
        ? await getHotTopics(selectedSource)
        : await getHotTopics();
      if (res.success) {
        setTopics(res.topics || []);
      } else {
        setError(res.message || "加载失败");
      }
    } catch (e) {
      setError("加载热点话题失败");
    } finally {
      setLoading(false);
    }
  };

  const formatHotValue = (value: number) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
    return String(value);
  };

  const handleTopicClick = (topic: HotTopic) => {
    if (onSelectTopic) {
      onSelectTopic(topic.title);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">热点话题</h1>
          <p className="text-white/50 text-sm mt-1">追踪各平台热议话题，获取创作灵感</p>
        </div>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-medium transition-colors"
        >
          返回
        </button>
      </div>

      {/* Source Filter */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setSelectedSource(null)}
          className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
            selectedSource === null
              ? "bg-purple-600 text-white"
              : "bg-white/5 text-white/60 hover:bg-white/10"
          }`}
        >
          全部
        </button>
        {sources.map((source) => (
          <button
            key={source.id}
            onClick={() => setSelectedSource(source.id)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2 ${
              selectedSource === source.id
                ? "bg-purple-600 text-white"
                : "bg-white/5 text-white/60 hover:bg-white/10"
            }`}
          >
            <span>{source.icon}</span>
            <span>{source.name}</span>
          </button>
        ))}
        <button
          onClick={loadTopics}
          className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white/60 rounded-xl text-sm transition-colors"
        >
          刷新
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center h-64">
          <div className="text-white/60">加载中...</div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-6 text-red-400 text-center">
          {error}
        </div>
      )}

      {/* Topics Grid */}
      {!loading && !error && (
        <div className="grid grid-cols-2 gap-4">
          {topics.map((topic, index) => (
            <button
              key={`${topic.source}-${index}`}
              onClick={() => handleTopicClick(topic)}
              className="p-5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl text-left transition-all group"
            >
              <div className="flex items-start gap-4">
                <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold ${
                  topic.rank <= 3 ? "bg-red-500/20 text-red-400" :
                  topic.rank <= 10 ? "bg-orange-500/20 text-orange-400" :
                  "bg-white/10 text-white/60"
                }`}>
                  {topic.rank}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-white font-medium group-hover:text-purple-300 transition-colors line-clamp-2">
                    {topic.title}
                  </div>
                  <div className="flex items-center gap-3 mt-2">
                    <span className="text-white/40 text-sm">
                      {formatHotValue(topic.hot_value)}
                    </span>
                    {topic.source && (
                      <span className="px-2 py-0.5 bg-purple-500/20 text-purple-300 rounded text-xs">
                        {topic.source === "weibo" ? "微博" :
                         topic.source === "douyin" ? "抖音" :
                         topic.source === "toutiao" ? "头条" : topic.source}
                      </span>
                    )}
                    {topic.category && (
                      <span className="px-2 py-0.5 bg-white/10 text-white/60 rounded text-xs">
                        {topic.category}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && topics.length === 0 && (
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-12 border border-white/10 text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-medium text-white mb-2">暂无热点话题</h3>
          <p className="text-white/50 mb-6">稍后再试或尝试其他来源</p>
          <button
            onClick={loadTopics}
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium transition-colors"
          >
            刷新
          </button>
        </div>
      )}
    </div>
  );
}
