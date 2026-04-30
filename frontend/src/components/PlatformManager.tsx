import { useState, useEffect } from "react";

interface PlatformAccount {
  id: number;
  platform: string;
  account_name: string;
  account_id: string;
  status: string;
  followers: number;
  created_at: string;
}

interface Props {
  token: string;
  onBack: () => void;
}

export default function PlatformManager({ token, onBack }: Props) {
  const [accounts, setAccounts] = useState<PlatformAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [oauthUrl, setOauthUrl] = useState("");
  const [oauthPlatform, setOauthPlatform] = useState("");
  const [platformForm, setPlatformForm] = useState({
    platform: "wechat_public",
    account_name: "",
    account_id: "",
    access_token: "",
    refresh_token: "",
  });

  const platformNames: Record<string, string> = {
    wechat_public: "公众号",
    toutiao: "头条号",
    xiaohongshu: "小红书",
    zhihu: "知乎",
    baijiahao: "百家号",
    bilibili: "B站",
    douyin: "抖音",
  };

  useEffect(() => {
    fetchAccounts();
  }, [token]);

  const fetchAccounts = async () => {
    try {
      const res = await fetch("/api/platforms/accounts", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.success) {
        setAccounts(data.accounts || []);
      }
    } catch (error) {
      console.error("获取平台账号失败:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnectOAuth = async (platform: string) => {
    try {
      const res = await fetch(`/api/oauth/${platform}/authorize`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.success) {
        // 打开 OAuth 授权页面
        window.open(data.authorization_url, "_blank", "width=600,height=700");
      }
    } catch (error) {
      console.error("获取授权 URL 失败:", error);
    }
  };

  const handleManualAdd = async () => {
    try {
      const res = await fetch("/api/platforms/accounts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(platformForm),
      });
      const data = await res.json();
      if (data.success) {
        setShowAddModal(false);
        setPlatformForm({
          platform: "wechat_public",
          account_name: "",
          account_id: "",
          access_token: "",
          refresh_token: "",
        });
        fetchAccounts();
      }
    } catch (error) {
      console.error("添加平台账号失败:", error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("确定要删除这个平台账号吗？")) return;
    try {
      const res = await fetch(`/api/platforms/accounts/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.success) {
        setAccounts(accounts.filter((a) => a.id !== id));
      }
    } catch (error) {
      console.error("删除平台账号失败:", error);
    }
  };

  const handleUpdate = async (id: number, followers: number) => {
    try {
      const res = await fetch(`/api/platforms/accounts/${id}?followers=${followers}`, {
        method: "PUT",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.success) {
        fetchAccounts();
      }
    } catch (error) {
      console.error("更新平台账号失败:", error);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">平台管理</h1>
          <p className="text-white/50 text-sm mt-1">管理您的社交媒体平台账号</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-sm font-medium transition-colors"
          >
            手动添加
          </button>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-medium transition-colors"
          >
            返回
          </button>
        </div>
      </div>

      {/* Platform Cards */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-white/60">加载中...</div>
        </div>
      ) : accounts.length === 0 ? (
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-12 border border-white/10 text-center">
          <div className="text-6xl mb-4">🔗</div>
          <h3 className="text-xl font-medium text-white mb-2">尚未连接任何平台</h3>
          <p className="text-white/50 mb-6">连接您的社交媒体平台，开始统一管理内容发布</p>
          <div className="flex justify-center gap-4">
            {["wechat_public", "toutiao", "xiaohongshu"].map((p) => (
              <button
                key={p}
                onClick={() => handleConnectOAuth(p)}
                className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium transition-colors"
              >
                连接 {platformNames[p] || p}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {accounts.map((account) => (
            <div
              key={account.id}
              className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center text-2xl">
                    {account.platform === "wechat_public" && "📝"}
                    {account.platform === "toutiao" && "📰"}
                    {account.platform === "xiaohongshu" && "📕"}
                    {account.platform === "zhihu" && "💬"}
                    {account.platform === "douyin" && "🎵"}
                    {account.platform === "bilibili" && "📺"}
                  </div>
                  <div>
                    <h3 className="text-white font-medium">
                      {platformNames[account.platform] || account.platform}
                    </h3>
                    <p className="text-white/50 text-sm">{account.account_name || account.account_id}</p>
                  </div>
                </div>
                <span
                  className={`px-2 py-1 rounded text-xs ${
                    account.status === "active"
                      ? "bg-green-500/20 text-green-400"
                      : "bg-yellow-500/20 text-yellow-400"
                  }`}
                >
                  {account.status === "active" ? "已连接" : "未连接"}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <div className="text-white/50">
                  粉丝: <span className="text-white">{account.followers || 0}</span>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      const newFollowers = prompt("更新粉丝数:", String(account.followers || 0));
                      if (newFollowers) handleUpdate(account.id, Number(newFollowers));
                    }}
                    className="px-3 py-1 bg-white/10 hover:bg-white/20 text-white/70 rounded-lg transition-colors"
                  >
                    更新粉丝
                  </button>
                  <button
                    onClick={() => handleDelete(account.id)}
                    className="px-3 py-1 bg-red-500/20 hover:bg-red-500/40 text-red-400 rounded-lg transition-colors"
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-gray-900 rounded-2xl p-6 w-full max-w-md border border-white/10">
            <h3 className="text-xl font-medium text-white mb-4">添加平台账号</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-white/60 text-sm mb-1">平台</label>
                <select
                  value={platformForm.platform}
                  onChange={(e) => setPlatformForm({ ...platformForm, platform: e.target.value })}
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white"
                >
                  <option value="wechat_public">公众号</option>
                  <option value="toutiao">头条号</option>
                  <option value="xiaohongshu">小红书</option>
                  <option value="zhihu">知乎</option>
                  <option value="baijiahao">百家号</option>
                  <option value="bilibili">B站</option>
                </select>
              </div>
              <div>
                <label className="block text-white/60 text-sm mb-1">账号名称</label>
                <input
                  type="text"
                  value={platformForm.account_name}
                  onChange={(e) => setPlatformForm({ ...platformForm, account_name: e.target.value })}
                  placeholder="如：我的公众号"
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white"
                />
              </div>
              <div>
                <label className="block text-white/60 text-sm mb-1">账号ID</label>
                <input
                  type="text"
                  value={platformForm.account_id}
                  onChange={(e) => setPlatformForm({ ...platformForm, account_id: e.target.value })}
                  placeholder="平台提供的账号ID"
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  onClick={handleManualAdd}
                  className="flex-1 py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-xl transition-colors"
                >
                  添加
                </button>
                <button
                  onClick={() => setShowAddModal(false)}
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
