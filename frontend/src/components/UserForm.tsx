import { useState } from "react";
import { UserInput } from "../api";

interface Props {
  onSubmit: (input: UserInput) => void;
  disabled?: boolean;
}

const CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "西安", "南京", "重庆", "苏州", "天津", "郑州", "长沙", "合肥", "石家庄", "昆明", "哈尔滨", "沈阳", "厦门", "济南", "青岛", "福州", "东莞", "佛山", "宁波", "无锡"];
const TIME_OPTIONS = ["每天少于1小时", "每天1-2小时", "每天2-4小时", "每天4小时以上"];
const RISK_OPTIONS = ["保守型", "稳健型", "进取型"];
const STATUS_OPTIONS = ["在职", "学生", "自由职业", "失业"];
const INDUSTRY_OPTIONS = ["互联网", "金融", "教育", "医疗", "制造", "零售", "媒体", "建筑", "政府", "法律", "咨询", "其他"];
const EXP_OPTIONS = ["1年以下", "1-3年", "3-5年", "5-10年", "10年以上"];
const SIDE_EXP_OPTIONS = ["无经验", "有一些", "经验丰富"];
const BUDGET_OPTIONS = ["500元以下", "500-2000元", "2000-5000元", "5000元以上"];
const WORK_MODE_OPTIONS = ["线上为主", "线下为主", "线上线下结合"];

export default function UserForm({ onSubmit, disabled }: Props) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [city, setCity] = useState("上海");
  const [skills, setSkills] = useState("");
  const [time, setTime] = useState("每天1-2小时");
  const [risk, setRisk] = useState("稳健型");
  const [avoidAppear, setAvoidAppear] = useState(false);
  const [goal, setGoal] = useState(5000);
  // 高级字段
  const [status, setStatus] = useState("在职");
  const [industry, setIndustry] = useState("互联网");
  const [workExp, setWorkExp] = useState("1-3年");
  const [sideExp, setSideExp] = useState("无经验");
  const [budget, setBudget] = useState("500-2000元");
  const [workMode, setWorkMode] = useState("线上为主");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      city,
      skills: skills.split(",").map(s => s.trim()).filter(Boolean),
      available_time: time,
      risk_preference: risk,
      avoid_appearing: avoidAppear,
      monthly_goal: goal,
      employment_status: status,
      industry,
      work_experience: workExp,
      side_hustle_exp: sideExp,
      startup_budget: budget,
      work_mode: workMode,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-10">
      {/* 基础信息 */}
      <div className="space-y-8">
        {/* 城市 + 月目标 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-3">
            <label className="block text-xl font-semibold text-gray-700">📍 所在城市</label>
            <select
              value={city}
              onChange={e => setCity(e.target.value)}
              disabled={disabled}
              className="w-full px-6 py-5 text-xl border-2 border-gray-200 rounded-2xl focus:border-purple-400 focus:ring-0 bg-white transition-colors cursor-pointer"
            >
              {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="space-y-3">
            <label className="block text-xl font-semibold text-gray-700">💰 月收入目标</label>
            <div className="relative">
              <input
                type="number"
                value={goal}
                onChange={e => setGoal(Number(e.target.value))}
                disabled={disabled}
                min="1000"
                max="100000"
                className="w-full px-6 py-5 text-xl border-2 border-gray-200 rounded-2xl focus:border-purple-400 focus:ring-0 transition-colors"
              />
              <span className="absolute right-6 top-1/2 -translate-y-1/2 text-gray-400 text-xl">元/月</span>
            </div>
          </div>
        </div>

        {/* 技能 */}
        <div className="space-y-3">
          <label className="block text-xl font-semibold text-gray-700">
            🛠️ 拥有技能 <span className="text-gray-400 text-base font-normal">(用逗号分隔)</span>
          </label>
          <input
            type="text"
            value={skills}
            onChange={e => setSkills(e.target.value)}
            disabled={disabled}
            placeholder="如: Python, Excel, 剪辑, 设计, 写作"
            className="w-full px-6 py-5 text-xl border-2 border-gray-200 rounded-2xl focus:border-purple-400 focus:ring-0 transition-colors"
          />
          <p className="text-base text-gray-500">描述您的技能，我们将为您精准匹配适合的副业方向</p>
        </div>

        {/* 时间 + 风险 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-3">
            <label className="block text-xl font-semibold text-gray-700">⏰ 每天可用时间</label>
            <select
              value={time}
              onChange={e => setTime(e.target.value)}
              disabled={disabled}
              className="w-full px-6 py-5 text-xl border-2 border-gray-200 rounded-2xl focus:border-purple-400 focus:ring-0 bg-white transition-colors cursor-pointer"
            >
              {TIME_OPTIONS.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="space-y-3">
            <label className="block text-xl font-semibold text-gray-700">📊 风险偏好</label>
            <select
              value={risk}
              onChange={e => setRisk(e.target.value)}
              disabled={disabled}
              className="w-full px-6 py-5 text-xl border-2 border-gray-200 rounded-2xl focus:border-purple-400 focus:ring-0 bg-white transition-colors cursor-pointer"
            >
              {RISK_OPTIONS.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
        </div>

        {/* 露脸偏好 */}
        <div className="flex items-center p-6 bg-gray-50 rounded-2xl">
          <input
            type="checkbox"
            id="avoidAppear"
            checked={avoidAppear}
            onChange={e => setAvoidAppear(e.target.checked)}
            disabled={disabled}
            className="w-7 h-7 text-purple-600 border-2 border-gray-300 rounded-lg focus:ring-purple-500 cursor-pointer"
          />
          <label htmlFor="avoidAppear" className="ml-5 text-xl text-gray-700 cursor-pointer">
            🙅 我不想露脸（优先推荐不需要抛头露面的副业）
          </label>
        </div>
      </div>

      {/* 分隔线 + 高级选项 */}
      <div className="border-t-2 border-gray-100 pt-8">
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="w-full flex items-center justify-between text-left px-2 py-3 hover:bg-gray-50 rounded-xl transition-colors"
        >
          <span className="text-xl font-semibold text-gray-500 flex items-center gap-3">
            <span className="text-2xl">⚡</span> 高级选项（让推荐更精准）
          </span>
          <span className={`text-gray-400 text-2xl transition-transform ${showAdvanced ? "rotate-180" : ""}`}>›</span>
        </button>

        {showAdvanced && (
          <div className="mt-6 space-y-8 animate-in">
            {/* 身份状态 + 行业 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-3">
                <label className="block text-xl font-semibold text-gray-700">👔 身份状态</label>
                <select
                  value={status}
                  onChange={e => setStatus(e.target.value)}
                  disabled={disabled}
                  className="w-full px-6 py-5 text-xl border-2 border-gray-200 rounded-2xl focus:border-purple-400 focus:ring-0 bg-white transition-colors cursor-pointer"
                >
                  {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div className="space-y-3">
                <label className="block text-xl font-semibold text-gray-700">🏢 所在行业</label>
                <select
                  value={industry}
                  onChange={e => setIndustry(e.target.value)}
                  disabled={disabled}
                  className="w-full px-6 py-5 text-xl border-2 border-gray-200 rounded-2xl focus:border-purple-400 focus:ring-0 bg-white transition-colors cursor-pointer"
                >
                  {INDUSTRY_OPTIONS.map(i => <option key={i} value={i}>{i}</option>)}
                </select>
              </div>
            </div>

            {/* 工作经验 + 副业经验 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-3">
                <label className="block text-xl font-semibold text-gray-700">💼 工作经验</label>
                <select
                  value={workExp}
                  onChange={e => setWorkExp(e.target.value)}
                  disabled={disabled}
                  className="w-full px-6 py-5 text-xl border-2 border-gray-200 rounded-2xl focus:border-purple-400 focus:ring-0 bg-white transition-colors cursor-pointer"
                >
                  {EXP_OPTIONS.map(e => <option key={e} value={e}>{e}</option>)}
                </select>
              </div>
              <div className="space-y-3">
                <label className="block text-xl font-semibold text-gray-700">🎯 副业经验</label>
                <select
                  value={sideExp}
                  onChange={e => setSideExp(e.target.value)}
                  disabled={disabled}
                  className="w-full px-6 py-5 text-xl border-2 border-gray-200 rounded-2xl focus:border-purple-400 focus:ring-0 bg-white transition-colors cursor-pointer"
                >
                  {SIDE_EXP_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </div>

            {/* 启动预算 + 工作方式 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-3">
                <label className="block text-xl font-semibold text-gray-700">💳 启动预算</label>
                <select
                  value={budget}
                  onChange={e => setBudget(e.target.value)}
                  disabled={disabled}
                  className="w-full px-6 py-5 text-xl border-2 border-gray-200 rounded-2xl focus:border-purple-400 focus:ring-0 bg-white transition-colors cursor-pointer"
                >
                  {BUDGET_OPTIONS.map(b => <option key={b} value={b}>{b}</option>)}
                </select>
              </div>
              <div className="space-y-3">
                <label className="block text-xl font-semibold text-gray-700">🌐 工作方式偏好</label>
                <select
                  value={workMode}
                  onChange={e => setWorkMode(e.target.value)}
                  disabled={disabled}
                  className="w-full px-6 py-5 text-xl border-2 border-gray-200 rounded-2xl focus:border-purple-400 focus:ring-0 bg-white transition-colors cursor-pointer"
                >
                  {WORK_MODE_OPTIONS.map(m => <option key={m} value={m}>{m}</option>)}
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 提交按钮 */}
      <button
        type="submit"
        disabled={disabled}
        className="w-full py-6 text-2xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold rounded-2xl shadow-lg hover:from-purple-700 hover:to-indigo-700 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {disabled ? (
          <span className="flex items-center justify-center gap-3">
            <svg className="animate-spin h-6 w-6" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            分析中...
          </span>
        ) : (
          "🚀 获取精准推荐"
        )}
      </button>
    </form>
  );
}
