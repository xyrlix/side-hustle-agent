import { useState } from "react";
import { login as apiLogin, register as apiRegister } from "../api";

interface Props {
  onClose: () => void;
  onLogin: (token: string, user: any) => void;
}

export default function LoginModal({ onClose, onLogin }: Props) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const result = isLogin
        ? await apiLogin(username, password)
        : await apiRegister(username, password, email);

      if (result.success && result.token) {
        localStorage.setItem("auth_token", result.token);
        localStorage.setItem("auth_user", JSON.stringify(result.user));
        onLogin(result.token, result.user);
        onClose();
      } else {
        setError(result.message || "操作失败");
      }
    } catch {
      setError("网络错误，请重试");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-[#1a1a3e]/95 backdrop-blur-xl border border-white/10 rounded-3xl w-full max-w-md shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-8 py-6 border-b border-white/10 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-white flex items-center gap-3">
            <span className="text-3xl">{isLogin ? "🔐" : "📝"}</span>
            {isLogin ? "登录" : "注册"}
          </h2>
          <button
            onClick={onClose}
            className="text-white/40 hover:text-white text-3xl leading-none transition-colors"
          >
            ×
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-8 space-y-6">
          {error && (
            <div className="bg-red-500/20 border border-red-500/30 rounded-xl px-4 py-3 text-red-400 text-center">
              {error}
            </div>
          )}

          <div>
            <label className="block text-white/70 text-sm font-medium mb-2">用户名</label>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="请输入用户名"
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:border-purple-500 focus:outline-none transition-colors"
              required
            />
          </div>

          <div>
            <label className="block text-white/70 text-sm font-medium mb-2">密码</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="请输入密码"
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:border-purple-500 focus:outline-none transition-colors"
              required
            />
          </div>

          {!isLogin && (
            <div>
              <label className="block text-white/70 text-sm font-medium mb-2">邮箱（可选）</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="请输入邮箱"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:border-purple-500 focus:outline-none transition-colors"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !username || !password}
            className="w-full py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-purple-500/30"
          >
            {loading ? "处理中..." : isLogin ? "登录" : "注册"}
          </button>

          <div className="text-center">
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setError("");
              }}
              className="text-purple-400 hover:text-purple-300 text-sm transition-colors"
            >
              {isLogin ? "没有账号？立即注册" : "已有账号？立即登录"}
            </button>
          </div>

          {isLogin && (
            <div className="text-center text-white/40 text-xs mt-4">
              默认管理员：admin / admin123
            </div>
          )}
        </form>
      </div>
    </div>
  );
}