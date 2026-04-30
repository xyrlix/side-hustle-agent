import { useState, useEffect } from "react";

interface ScheduledPost {
  id: number;
  content_id: number;
  title?: string;
  body?: string;
  platform: string;
  scheduled_at: string;
  status: string;
  created_at: string;
}

interface ContentItem {
  id: number;
  title: string;
  status: string;
}

interface Props {
  token: string;
  onBack: () => void;
}

export default function ScheduledPostsManager({ token, onBack }: Props) {
  const [posts, setPosts] = useState<ScheduledPost[]>([]);
  const [contents, setContents] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filter, setFilter] = useState<"all" | "pending" | "completed" | "failed">("all");

  const [newPost, setNewPost] = useState({
    content_id: 0,
    platform: "wechat_public",
    scheduled_at: "",
  });

  const platformNames: Record<string, string> = {
    wechat_public: "公众号",
    toutiao: "头条号",
    xiaohongshu: "小红书",
    zhihu: "知乎",
    baijiahao: "百家号",
    bilibili: "B站",
  };

  useEffect(() => {
    fetchData();
  }, [token, filter]);

  const fetchData = async () => {
    setLoading(true);
    try {
      // 获取定时任务
      const postsRes = await fetch(
        filter === "all" ? "/api/scheduled-posts" : `/api/scheduled-posts?status=${filter}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const postsData = await postsRes.json();
      if (postsData.success) {
        setPosts(postsData.scheduled_posts || []);
      }

      // 获取内容列表（用于选择）
      const contentsRes = await fetch("/api/content?limit=100", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const contentsData = await contentsRes.json();
      if (contentsData.success) {
        setContents(contentsData.contents || []);
      }
    } catch (error) {
      console.error("获取数据失败:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!newPost.content_id || !newPost.platform || !newPost.scheduled_at) {
      alert("请填写完整信息");
      return;
    }

    try {
      const res = await fetch("/api/scheduled-posts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(newPost),
      });
      const data = await res.json();
      if (data.success) {
        setShowCreateModal(false);
        setNewPost({ content_id: 0, platform: "wechat_public", scheduled_at: "" });
        fetchData();
      } else {
        alert(data.message || "创建失败");
      }
    } catch (error) {
      console.error("创建失败:", error);
    }
  };

  const handleCancel = async (postId: number) => {
    if (!confirm("确定要取消这个定时发布任务吗？")) return;

    try {
      const res = await fetch(`/api/scheduled-posts/${postId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.success) {
        fetchData();
      } else {
        alert(data.message || "取消失败");
      }
    } catch (error) {
      console.error("取消失败:", error);
    }
  };

  const formatDateTime = (isoString: string) => {
    const d = new Date(isoString);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">定时发布</h1>
          <p className="text-white/50 text-sm mt-1">管理您的内容定时发布任务</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-sm font-medium transition-colors"
          >
            创建定时发布
          </button>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-medium transition-colors"
          >
            返回
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        {(["all", "pending", "completed", "failed"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
              filter === f
                ? "bg-purple-600 text-white"
                : "bg-white/5 text-white/60 hover:bg-white/10"
            }`}
          >
            {f === "all" ? "全部" : f === "pending" ? "待发布" : f === "completed" ? "已发布" : "失败"}
          </button>
        ))}
      </div>

      {/* Posts List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-white/60">加载中...</div>
        </div>
      ) : posts.length === 0 ? (
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-12 border border-white/10 text-center">
          <div className="text-6xl mb-4">📅</div>
          <h3 className="text-xl font-medium text-white mb-2">暂无定时发布任务</h3>
          <p className="text-white/50 mb-6">创建您的第一个定时发布任务</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium transition-colors"
          >
            创建定时发布
          </button>
        </div>
      ) : (
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left px-6 py-4 text-white/60 text-sm font-medium">内容</th>
                <th className="text-left px-6 py-4 text-white/60 text-sm font-medium">平台</th>
                <th className="text-left px-6 py-4 text-white/60 text-sm font-medium">定时时间</th>
                <th className="text-left px-6 py-4 text-white/60 text-sm font-medium">状态</th>
                <th className="text-left px-6 py-4 text-white/60 text-sm font-medium">操作</th>
              </tr>
            </thead>
            <tbody>
              {posts.map((post) => (
                <tr key={post.id} className="border-b border-white/5 last:border-0">
                  <td className="px-6 py-4">
                    <div className="text-white font-medium">{post.title || `内容 #${post.content_id}`}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded text-sm">
                      {platformNames[post.platform] || post.platform}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-white/80">
                    {formatDateTime(post.scheduled_at)}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`px-2 py-1 rounded text-sm ${
                        post.status === "pending"
                          ? "bg-yellow-500/20 text-yellow-300"
                          : post.status === "completed"
                          ? "bg-green-500/20 text-green-300"
                          : "bg-red-500/20 text-red-300"
                      }`}
                    >
                      {post.status === "pending" ? "待发布" : post.status === "completed" ? "已发布" : "失败"}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {post.status === "pending" && (
                      <button
                        onClick={() => handleCancel(post.id)}
                        className="px-3 py-1 bg-red-500/20 hover:bg-red-500/40 text-red-300 rounded-lg text-sm transition-colors"
                      >
                        取消
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-gray-900 rounded-2xl p-6 w-full max-w-md border border-white/10">
            <h3 className="text-xl font-medium text-white mb-4">创建定时发布</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-white/60 text-sm mb-1">选择内容</label>
                <select
                  value={newPost.content_id}
                  onChange={(e) => setNewPost({ ...newPost, content_id: Number(e.target.value) })}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white"
                >
                  <option value={0}>请选择内容</option>
                  {contents
                    .filter((c) => c.status === "draft")
                    .map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.title}
                      </option>
                    ))}
                </select>
              </div>
              <div>
                <label className="block text-white/60 text-sm mb-1">发布平台</label>
                <select
                  value={newPost.platform}
                  onChange={(e) => setNewPost({ ...newPost, platform: e.target.value })}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white"
                >
                  <option value="wechat_public">公众号</option>
                  <option value="toutiao">头条号</option>
                  <option value="xiaohongshu">小红书</option>
                  <option value="zhihu">知乎</option>
                </select>
              </div>
              <div>
                <label className="block text-white/60 text-sm mb-1">定时时间</label>
                <input
                  type="datetime-local"
                  value={newPost.scheduled_at}
                  onChange={(e) => setNewPost({ ...newPost, scheduled_at: e.target.value })}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  onClick={handleCreate}
                  className="flex-1 py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-xl transition-colors"
                >
                  创建
                </button>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl transition-colors"
                >
                  取消
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
