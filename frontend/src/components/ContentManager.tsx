import { useState, useEffect } from "react";

interface Props {
  token?: string;
  onBack?: () => void;
}

interface Content {
  id: number;
  title: string;
  summary: string;
  status: string;
  tags: string[];
  category: string;
  views: number;
  likes: number;
  revenue: number;
  created_at: string;
  updated_at: string;
}

interface Platform {
  id: string;
  name: string;
  content_format: string[];
}

interface PublishLog {
  id: number;
  platform: string;
  status: string;
  published_url: string;
  published_at: string;
  created_at: string;
}

const STATUS_CONFIG: Record<string, { label: string; bg: string; text: string; border: string }> = {
  draft: { label: "草稿", bg: "bg-gray-500/10", text: "text-gray-400", border: "border-gray-500/30" },
  pending: { label: "待发布", bg: "bg-yellow-500/10", text: "text-yellow-400", border: "border-yellow-500/30" },
  published: { label: "已发布", bg: "bg-green-500/10", text: "text-green-400", border: "border-green-500/30" },
  failed: { label: "失败", bg: "bg-red-500/10", text: "text-red-400", border: "border-red-500/30" },
};

function formatDate(dateStr: string): string {
  if (!dateStr) return "-";
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, "0")}`;
}

export default function ContentManager(_props?: Props) {
  const [contents, setContents] = useState<Content[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [showEditor, setShowEditor] = useState(false);
  const [editingContent, setEditingContent] = useState<Content | null>(null);
  const [formData, setFormData] = useState({
    title: "",
    body: "",
    summary: "",
    tags: "",
    category: "",
  });
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [selectedPlatform, setSelectedPlatform] = useState<string>("");
  const [showPublishModal, setShowPublishModal] = useState(false);
  const [publishLogs, setPublishLogs] = useState<PublishLog[]>([]);
  const [showAIGenerate, setShowAIGenerate] = useState(false);
  const [aiGenerating, setAIGenerating] = useState(false);
  const [aiFormData, setAiFormData] = useState({
    topic: "",
    platform: "wechat_public",
    style: "专业",
    keywords: "",
    length: "中等",
  });

  const token = localStorage.getItem("auth_token");

  useEffect(() => {
    loadContents();
    loadPlatforms();
  }, [statusFilter]);

  const loadContents = async () => {
    setLoading(true);
    try {
      const url = statusFilter
        ? `http://localhost:8000/api/content?status=${statusFilter}&limit=100`
        : "http://localhost:8000/api/content?limit=100";
      const res = await fetch(url, { headers: { "Authorization": `Bearer ${token}` } });
      const data = await res.json();
      if (data.success) {
        setContents(data.contents || []);
      }
    } catch (e) {
      console.error("加载内容失败:", e);
    } finally {
      setLoading(false);
    }
  };

  const loadPlatforms = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/platforms");
      const data = await res.json();
      if (data.success) {
        setPlatforms(data.platforms || []);
      }
    } catch (e) {
      console.error("加载平台失败:", e);
    }
  };

  const handleCreate = () => {
    setEditingContent(null);
    setFormData({ title: "", body: "", summary: "", tags: "", category: "" });
    setShowEditor(true);
  };

  const handleEdit = (content: Content) => {
    // 编辑时获取完整数据（包括正文）
    fetch(`http://localhost:8000/api/content/${content.id}`, {
      headers: { "Authorization": `Bearer ${token}` },
    })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.content) {
          const fullContent = data.content;
          setEditingContent(fullContent);
          setFormData({
            title: fullContent.title,
            body: fullContent.body || "",
            summary: fullContent.summary || "",
            tags: (fullContent.tags || []).join(", "),
            category: fullContent.category || "",
          });
        } else {
          // 后备：使用列表数据
          setEditingContent(content);
          setFormData({
            title: content.title,
            body: "",
            summary: content.summary || "",
            tags: (content.tags || []).join(", "),
            category: content.category || "",
          });
        }
        setShowEditor(true);
        loadPublishLogs(content.id);
      })
      .catch(() => {
        setEditingContent(content);
        setFormData({
          title: content.title,
          body: "",
          summary: content.summary || "",
          tags: (content.tags || []).join(", "),
          category: content.category || "",
        });
        setShowEditor(true);
      });
  };

  const loadPublishLogs = async (contentId: number) => {
    try {
      const res = await fetch(`http://localhost:8000/api/content/${contentId}/logs`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.success) {
        setPublishLogs(data.logs || []);
      }
    } catch (e) {
      console.error("加载发布日志失败:", e);
    }
  };

  const handleSave = async () => {
    if (!formData.title.trim()) {
      alert("标题不能为空");
      return;
    }

    const tags = formData.tags.split(",").map(t => t.trim()).filter(Boolean);
    const payload = {
      title: formData.title,
      body: formData.body,
      summary: formData.summary,
      tags,
      category: formData.category,
    };

    try {
      const url = editingContent
        ? `http://localhost:8000/api/content/${editingContent.id}`
        : "http://localhost:8000/api/content";
      const method = editingContent ? "PUT" : "POST";
      const res = await fetch(url, {
        method,
        headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (data.success) {
        setShowEditor(false);
        loadContents();
      } else {
        alert(data.message || "保存失败");
      }
    } catch (e) {
      alert("保存失败");
    }
  };

  const handleDelete = async (contentId: number) => {
    if (!confirm("确定要删除这篇内容吗？")) return;
    try {
      const res = await fetch(`http://localhost:8000/api/content/${contentId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.success) {
        loadContents();
      } else {
        alert(data.message || "删除失败");
      }
    } catch (e) {
      alert("删除失败");
    }
  };

  const handlePublish = async () => {
    if (!selectedPlatform || !editingContent) return;
    try {
      const res = await fetch(
        `http://localhost:8000/api/content/${editingContent.id}/publish?platform=${selectedPlatform}`,
        { method: "POST", headers: { "Authorization": `Bearer ${token}` } }
      );
      const data = await res.json();
      if (data.success) {
        setShowPublishModal(false);
        loadPublishLogs(editingContent.id);
        alert("发布成功！");
      } else {
        alert(data.message || "发布失败");
      }
    } catch (e) {
      alert("发布失败");
    }
  };

  const statusCounts = {
    all: contents.length,
    draft: contents.filter(c => c.status === "draft").length,
    pending: contents.filter(c => c.status === "pending").length,
    published: contents.filter(c => c.status === "published").length,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-950 to-indigo-950 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white">内容管理</h1>
            <p className="text-white/40 mt-2">创作、编辑、发布你的内容到各个平台</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowAIGenerate(true)}
              className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl font-medium flex items-center gap-2 shadow-lg"
            >
              <span className="text-xl">🤖</span> AI 生成
            </button>
            <button
              onClick={handleCreate}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium flex items-center gap-2"
            >
              <span className="text-xl">+</span> 创建内容
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {[
            { key: "all", label: "全部", icon: "📄" },
            { key: "draft", label: "草稿", icon: "📝" },
            { key: "pending", label: "待发布", icon: "⏰" },
            { key: "published", label: "已发布", icon: "✅" },
          ].map(({ key, label, icon }) => (
            <button
              key={key}
              onClick={() => setStatusFilter(key === "all" ? null : key)}
              className={`p-5 rounded-2xl border transition-all ${
                statusFilter === (key === "all" ? null : key)
                  ? "bg-purple-600/20 border-purple-500/50"
                  : "bg-white/5 border-white/10 hover:border-white/20"
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{icon}</span>
                <div>
                  <div className="text-2xl font-bold text-white">{statusCounts[key as keyof typeof statusCounts]}</div>
                  <div className="text-white/40 text-sm">{label}</div>
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Content List */}
        {loading ? (
          <div className="text-center py-20">
            <div className="text-white/50 text-xl">加载中...</div>
          </div>
        ) : contents.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-6xl mb-4 opacity-30">📝</div>
            <div className="text-white/40 text-xl mb-6">暂无内容</div>
            <button onClick={handleCreate} className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl">
              创建第一篇内容
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {contents.map((content) => {
              const config = STATUS_CONFIG[content.status] || STATUS_CONFIG.draft;
              return (
                <div
                  key={content.id}
                  className="bg-white/5 border border-white/10 rounded-2xl p-6 hover:border-purple-500/30 transition-all"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-bold text-white truncate">{content.title}</h3>
                        <span className={`px-3 py-1 rounded-full text-xs border ${config.bg} ${config.text} ${config.border} shrink-0`}>
                          {config.label}
                        </span>
                      </div>
                      {content.summary && (
                        <p className="text-white/50 text-sm mb-3 line-clamp-2">{content.summary}</p>
                      )}
                      <div className="flex items-center gap-4 text-white/30 text-sm">
                        <span>📅 {formatDate(content.created_at)}</span>
                        <span className="text-purple-400">👁 {content.views || 0}</span>
                        <span className="text-green-400">💰 ¥{content.revenue || 0}</span>
                      </div>
                      {(content.tags || []).length > 0 && (
                        <div className="flex gap-2 mt-3">
                          {(content.tags || []).slice(0, 4).map((tag, i) => (
                            <span key={i} className="px-2 py-0.5 bg-purple-500/20 text-purple-300 rounded text-xs">#{tag}</span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => handleEdit(content)}
                        className="px-4 py-2 bg-purple-600/30 hover:bg-purple-600/50 text-purple-300 rounded-lg text-sm"
                      >
                        编辑
                      </button>
                      {content.status !== "published" && (
                        <button
                          onClick={() => {
                            setEditingContent(content);
                            setShowPublishModal(true);
                          }}
                          className="px-4 py-2 bg-green-600/30 hover:bg-green-600/50 text-green-300 rounded-lg text-sm"
                        >
                          发布
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(content.id)}
                        className="px-4 py-2 bg-red-600/30 hover:bg-red-600/50 text-red-300 rounded-lg text-sm"
                      >
                        删除
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Editor Modal */}
      {showEditor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-8">
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm" onClick={() => setShowEditor(false)} />
          <div className="relative w-full max-w-3xl max-h-[90vh] bg-[#0f172a] border border-white/10 rounded-3xl overflow-hidden flex flex-col">
            <div className="px-8 py-6 border-b border-white/10 flex items-center justify-between shrink-0">
              <h2 className="text-2xl font-bold text-white">
                {editingContent ? "编辑内容" : "创建内容"}
              </h2>
              <button onClick={() => setShowEditor(false)} className="text-white/40 hover:text-white text-2xl w-10 h-10 flex items-center justify-center">×</button>
            </div>

            <div className="p-8 space-y-6 overflow-y-auto flex-1">
              <div>
                <label className="block text-white/60 mb-2 text-sm font-medium">标题</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white text-lg focus:border-purple-500 outline-none"
                  placeholder="输入内容标题..."
                />
              </div>
              <div>
                <label className="block text-white/60 mb-2 text-sm font-medium">正文</label>
                <textarea
                  value={formData.body}
                  onChange={(e) => setFormData({ ...formData, body: e.target.value })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white min-h-[200px] focus:border-purple-500 outline-none resize-none"
                  placeholder="输入内容正文..."
                />
              </div>
              <div>
                <label className="block text-white/60 mb-2 text-sm font-medium">摘要</label>
                <input
                  type="text"
                  value={formData.summary}
                  onChange={(e) => setFormData({ ...formData, summary: e.target.value })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:border-purple-500 outline-none"
                  placeholder="简短描述（可选）..."
                />
              </div>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-white/60 mb-2 text-sm font-medium">标签（逗号分隔）</label>
                  <input
                    type="text"
                    value={formData.tags}
                    onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:border-purple-500 outline-none"
                    placeholder="副业, 创业, 干货"
                  />
                </div>
                <div>
                  <label className="block text-white/60 mb-2 text-sm font-medium">分类</label>
                  <input
                    type="text"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:border-purple-500 outline-none"
                    placeholder="知识/生活/测评..."
                  />
                </div>
              </div>

              {/* Publish Logs */}
              {editingContent && publishLogs.length > 0 && (
                <div>
                  <label className="block text-white/60 mb-2 text-sm font-medium">发布历史</label>
                  <div className="space-y-2">
                    {publishLogs.map((log) => (
                      <div key={log.id} className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
                        <span className="text-white/60">{log.platform}</span>
                        <span className={`px-2 py-0.5 rounded text-xs ${
                          log.status === "success" ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"
                        }`}>
                          {log.status === "success" ? "成功" : "失败"}
                        </span>
                        {log.published_url && (
                          <a href={log.published_url} target="_blank" rel="noopener noreferrer" className="text-purple-400 text-sm hover:underline ml-auto">
                            查看 ↗
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="px-8 py-6 border-t border-white/10 flex items-center justify-between shrink-0 bg-[#0f172a]">
              <button onClick={() => setShowPublishModal(true)} className="px-6 py-3 bg-green-600/30 hover:bg-green-600/50 text-green-300 rounded-xl">
                发布到平台
              </button>
              <div className="flex items-center gap-3">
                <button onClick={() => setShowEditor(false)} className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white/70 rounded-xl">
                  取消
                </button>
                <button onClick={handleSave} className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium">
                  保存
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Publish Modal */}
      {showPublishModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-8">
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm" onClick={() => setShowPublishModal(false)} />
          <div className="relative w-full max-w-md bg-[#0f172a] border border-white/10 rounded-3xl overflow-hidden">
            <div className="px-8 py-6 border-b border-white/10 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">发布到平台</h2>
              <button onClick={() => setShowPublishModal(false)} className="text-white/40 hover:text-white text-2xl w-10 h-10 flex items-center justify-center">×</button>
            </div>
            <div className="p-8">
              <label className="block text-white/60 mb-4 text-sm font-medium">选择发布平台</label>
              <div className="grid grid-cols-2 gap-3">
                {platforms.map((platform) => (
                  <button
                    key={platform.id}
                    onClick={() => setSelectedPlatform(platform.id)}
                    className={`p-4 rounded-xl border text-left transition-all ${
                      selectedPlatform === platform.id
                        ? "bg-purple-600/20 border-purple-500/50 text-purple-300"
                        : "bg-white/5 border-white/10 text-white/70 hover:border-white/20"
                    }`}
                  >
                    <div className="font-medium">{platform.name}</div>
                    <div className="text-xs text-white/40 mt-1">{platform.content_format.join(", ")}</div>
                  </button>
                ))}
              </div>
            </div>
            <div className="px-8 py-6 border-t border-white/10 flex justify-end gap-3">
              <button onClick={() => setShowPublishModal(false)} className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white/70 rounded-xl">
                取消
              </button>
              <button
                onClick={handlePublish}
                disabled={!selectedPlatform}
                className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-xl font-medium disabled:opacity-50"
              >
                确认发布
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AI Generate Modal */}
      {showAIGenerate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-8">
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm" onClick={() => setShowAIGenerate(false)} />
          <div className="relative w-full max-w-lg bg-[#0f172a] border border-white/10 rounded-3xl overflow-hidden">
            <div className="px-8 py-6 border-b border-white/10 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">🤖 AI 内容生成</h2>
              <button onClick={() => setShowAIGenerate(false)} className="text-white/40 hover:text-white text-2xl w-10 h-10 flex items-center justify-center">×</button>
            </div>
            <div className="p-8 space-y-6">
              <div>
                <label className="block text-white/60 mb-2 text-sm font-medium">主题</label>
                <input
                  type="text"
                  value={aiFormData.topic}
                  onChange={(e) => setAiFormData({ ...aiFormData, topic: e.target.value })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:border-cyan-500 outline-none"
                  placeholder="输入内容主题，如：副业赚钱的5个方法"
                />
              </div>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-white/60 mb-2 text-sm font-medium">目标平台</label>
                  <select
                    value={aiFormData.platform}
                    onChange={(e) => setAiFormData({ ...aiFormData, platform: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:border-cyan-500 outline-none"
                  >
                    <option value="wechat_public">公众号</option>
                    <option value="toutiao">头条号</option>
                    <option value="xiaohongshu">小红书</option>
                    <option value="zhihu">知乎</option>
                  </select>
                </div>
                <div>
                  <label className="block text-white/60 mb-2 text-sm font-medium">风格</label>
                  <select
                    value={aiFormData.style}
                    onChange={(e) => setAiFormData({ ...aiFormData, style: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:border-cyan-500 outline-none"
                  >
                    <option value="专业">专业</option>
                    <option value="轻松">轻松</option>
                    <option value="幽默">幽默</option>
                    <option value="严谨">严谨</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-white/60 mb-2 text-sm font-medium">关键词</label>
                  <input
                    type="text"
                    value={aiFormData.keywords}
                    onChange={(e) => setAiFormData({ ...aiFormData, keywords: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:border-cyan-500 outline-none"
                    placeholder="逗号分隔"
                  />
                </div>
                <div>
                  <label className="block text-white/60 mb-2 text-sm font-medium">长度</label>
                  <select
                    value={aiFormData.length}
                    onChange={(e) => setAiFormData({ ...aiFormData, length: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:border-cyan-500 outline-none"
                  >
                    <option value="短">短（500-800字）</option>
                    <option value="中等">中等（1000-1500字）</option>
                    <option value="长">长（2000-3000字）</option>
                  </select>
                </div>
              </div>
            </div>
            <div className="px-8 py-6 border-t border-white/10 flex justify-end gap-3">
              <button onClick={() => setShowAIGenerate(false)} className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white/70 rounded-xl">
                取消
              </button>
              <button
                onClick={async () => {
                  if (!aiFormData.topic.trim()) {
                    alert("请输入内容主题");
                    return;
                  }
                  setAIGenerating(true);
                  try {
                    const keywords = aiFormData.keywords.split(",").map(k => k.trim()).filter(Boolean);
                    const res = await fetch("http://localhost:8000/api/ai/generate", {
                      method: "POST",
                      headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
                      body: JSON.stringify({
                        topic: aiFormData.topic,
                        platform: aiFormData.platform,
                        style: aiFormData.style,
                        keywords,
                        length: aiFormData.length,
                      }),
                    });
                    const data = await res.json();
                    if (data.success) {
                      setShowAIGenerate(false);
                      setShowEditor(true);
                      setEditingContent(data.content);
                      setFormData({
                        title: data.generated.title,
                        body: data.generated.body,
                        summary: data.generated.body?.slice(0, 200) || "",
                        tags: (data.generated.tags || []).join(", "),
                        category: aiFormData.platform,
                      });
                      loadContents();
                    } else {
                      alert(data.message || "生成失败");
                    }
                  } catch (e) {
                    alert("生成失败");
                  } finally {
                    setAIGenerating(false);
                  }
                }}
                disabled={aiGenerating}
                className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl font-medium disabled:opacity-50 flex items-center gap-2"
              >
                {aiGenerating ? (
                  <>
                    <span className="animate-spin">⏳</span> 生成中...
                  </>
                ) : (
                  <>
                    <span>🤖</span> 开始生成
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}