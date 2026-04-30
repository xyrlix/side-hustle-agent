import { useState, useEffect } from "react";
import { getAdminStats, getAdminUsers, getAdminRecommendations, getAdminHustleStats, getAdminUserProfiles } from "../api";

export default function AdminPanel({ onClose }: { onClose: () => void }) {
  const [activeTab, setActiveTab] = useState<"stats" | "users" | "history" | "hustles" | "profiles">("stats");
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [hustleStats, setHustleStats] = useState<any[]>([]);
  const [userProfiles, setUserProfiles] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsRes, usersRes, recsRes, hustleRes, profilesRes] = await Promise.all([
        getAdminStats(),
        getAdminUsers(),
        getAdminRecommendations(100),
        getAdminHustleStats(),
        getAdminUserProfiles(),
      ]);
      if (statsRes.success) setStats(statsRes.stats);
      if (usersRes.success) setUsers(usersRes.users);
      if (recsRes.success) setRecommendations(recsRes.recommendations);
      if (hustleRes.success) setHustleStats(hustleRes.stats || []);
      if (profilesRes.success) setUserProfiles(profilesRes.profiles);
    } catch (e) {
      console.error("加载数据失败:", e);
    }
    setLoading(false);
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return "-";
    const d = new Date(dateStr);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-[#0f172a]/95 backdrop-blur-xl border border-white/10 rounded-3xl w-full max-w-6xl max-h-[90vh] shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-8 py-6 border-b border-white/10 flex items-center justify-between shrink-0">
          <h2 className="text-2xl font-bold text-white flex items-center gap-3">
            <span className="text-3xl">⚙️</span> 管理后台
          </h2>
          <button
            onClick={onClose}
            className="text-white/40 hover:text-white text-3xl leading-none transition-colors"
          >
            ×
          </button>
        </div>

        {/* Tabs */}
        <div className="px-8 pt-4 flex gap-2 shrink-0 border-b border-white/10 flex-wrap">
          {([
            { id: "stats", label: "📊 统计" },
            { id: "users", label: "👥 用户" },
            { id: "hustles", label: "🔥 热门副业" },
            { id: "profiles", label: "👤 用户画像" },
            { id: "history", label: "📋 推荐记录" },
          ] as const).map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-xl font-medium transition-all text-sm ${
                activeTab === tab.id
                  ? "bg-purple-600 text-white"
                  : "text-white/50 hover:text-white hover:bg-white/10"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-8">
          {loading ? (
            <div className="text-center text-white/50 py-20">加载中...</div>
          ) : activeTab === "stats" && stats ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                { label: "总用户数", value: stats.total_users, icon: "👥", color: "purple" },
                { label: "总推荐次数", value: stats.total_recommendations, icon: "🎯", color: "green" },
                { label: "活跃用户", value: stats.total_users, icon: "✅", color: "blue" },
                { label: "本月新增", value: "—", icon: "📈", color: "amber" },
              ].map(item => (
                <div key={item.label} className="bg-white/5 border border-white/10 rounded-2xl p-6 text-center">
                  <div className="text-4xl mb-3">{item.icon}</div>
                  <div className="text-4xl font-bold text-white mb-1">{item.value}</div>
                  <div className="text-white/50 text-sm">{item.label}</div>
                </div>
              ))}
            </div>
          ) : activeTab === "users" ? (
            <div className="space-y-4">
              <div className="text-white/70 mb-4">共 {users.length} 个用户</div>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="text-white/50 text-sm border-b border-white/10">
                      <th className="py-3 px-4 font-medium">ID</th>
                      <th className="py-3 px-4 font-medium">用户名</th>
                      <th className="py-3 px-4 font-medium">邮箱</th>
                      <th className="py-3 px-4 font-medium">角色</th>
                      <th className="py-3 px-4 font-medium">注册时间</th>
                      <th className="py-3 px-4 font-medium">最后登录</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map(user => (
                      <tr key={user.id} className="text-white border-b border-white/5 hover:bg-white/5">
                        <td className="py-3 px-4">{user.id}</td>
                        <td className="py-3 px-4 font-medium">{user.username}</td>
                        <td className="py-3 px-4 text-white/60">{user.email || "-"}</td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            user.role === "admin" ? "bg-purple-500/30 text-purple-400" : "bg-blue-500/30 text-blue-400"
                          }`}>
                            {user.role}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-white/60">{formatDate(user.created_at)}</td>
                        <td className="py-3 px-4 text-white/60">{formatDate(user.last_login)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : activeTab === "hustles" ? (
            <div className="space-y-6">
              <h3 className="text-xl font-bold text-white mb-4">🔥 热门副业TOP10</h3>
              {hustleStats.length === 0 ? (
                <div className="text-white/50 text-center py-10">暂无数据</div>
              ) : (
                <div className="space-y-3">
                  {hustleStats.map((item: any, idx: number) => (
                    <div key={item.name} className="flex items-center gap-4 bg-white/5 rounded-xl p-4">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                        idx === 0 ? "bg-yellow-500/30 text-yellow-400" :
                        idx === 1 ? "bg-gray-400/30 text-gray-300" :
                        idx === 2 ? "bg-amber-600/30 text-amber-400" :
                        "bg-white/10 text-white/50"
                      }`}>
                        {idx + 1}
                      </div>
                      <div className="flex-1">
                        <div className="text-white font-medium">{item.name}</div>
                        <div className="text-white/40 text-sm">{item.count} 次推荐</div>
                      </div>
                      <div className="text-purple-400 font-bold text-lg">
                        {Math.round((item.count / (stats?.total_recommendations || 1)) * 100)}%
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : activeTab === "profiles" && userProfiles ? (
            <div className="space-y-8">
              <h3 className="text-xl font-bold text-white">👤 用户画像分析</h3>

              {/* 城市分布 */}
              <div className="bg-white/5 rounded-2xl p-6">
                <h4 className="text-lg font-medium text-purple-400 mb-4">📍 城市分布 TOP10</h4>
                <div className="space-y-2">
                  {(userProfiles.city_distribution || []).slice(0, 10).map(([city, count]: [string, number]) => (
                    <div key={city} className="flex items-center gap-3">
                      <div className="w-20 text-white/70 text-sm">{city}</div>
                      <div className="flex-1 h-6 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full"
                          style={{ width: `${(count / (stats?.total_recommendations || 1)) * 100}%` }}
                        />
                      </div>
                      <div className="w-12 text-white/50 text-sm text-right">{count}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 技能分布 */}
              <div className="bg-white/5 rounded-2xl p-6">
                <h4 className="text-lg font-medium text-blue-400 mb-4">🛠️ 热门技能 TOP15</h4>
                <div className="flex flex-wrap gap-2">
                  {(userProfiles.skill_distribution || []).slice(0, 15).map(([skill, count]: [string, number]) => (
                    <span key={skill} className="px-3 py-1.5 bg-blue-500/20 text-blue-400 rounded-full text-sm">
                      {skill} ({count})
                    </span>
                  ))}
                </div>
              </div>

              {/* 收入目标分布 */}
              <div className="bg-white/5 rounded-2xl p-6">
                <h4 className="text-lg font-medium text-green-400 mb-4">💰 月收入目标分布</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(userProfiles.goal_distribution || {}).map(([range, count]) => (
                    <div key={range} className="text-center">
                      <div className="text-3xl font-bold text-green-400">{count as number}</div>
                      <div className="text-white/50 text-sm">{range}元</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : activeTab === "history" ? (
            <div className="space-y-4">
              <div className="text-white/70 mb-4">共 {recommendations.length} 条推荐记录</div>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="text-white/50 text-sm border-b border-white/10">
                      <th className="py-3 px-4 font-medium">ID</th>
                      <th className="py-3 px-4 font-medium">用户</th>
                      <th className="py-3 px-4 font-medium">城市</th>
                      <th className="py-3 px-4 font-medium">推荐结果</th>
                      <th className="py-3 px-4 font-medium">时间</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recommendations.map(rec => (
                      <tr key={rec.id} className="text-white border-b border-white/5 hover:bg-white/5">
                        <td className="py-3 px-4">{rec.id}</td>
                        <td className="py-3 px-4 font-medium">{rec.user_id || "游客"}</td>
                        <td className="py-3 px-4">{rec.input_data?.city || "-"}</td>
                        <td className="py-3 px-4 text-white/60 max-w-xs truncate">
                          {rec.result_data?.selected_recommendation?.side_hustle?.name || "-"}
                        </td>
                        <td className="py-3 px-4 text-white/60">{formatDate(rec.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}