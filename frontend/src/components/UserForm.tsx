import { useState } from "react";
import { UserInput } from "../api";

interface Props {
  onSubmit: (input: UserInput) => void;
  disabled?: boolean;
}

const CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "西安", "南京", "重庆", "苏州", "天津", "郑州", "长沙", "合肥", "石家庄", "昆明", "哈尔滨", "沈阳", "厦门", "济南", "青岛", "福州", "东莞", "佛山", "宁波", "无锡"];
const TIME_OPTIONS = ["每天少于1小时", "每天1-2小时", "每天2-4小时", "每天4小时以上"];
const RISK_OPTIONS = ["保守型", "稳健型", "进取型"];

export default function UserForm({ onSubmit, disabled }: Props) {
  const [city, setCity] = useState("上海");
  const [skills, setSkills] = useState("");
  const [time, setTime] = useState("每天1-2小时");
  const [risk, setRisk] = useState("稳健型");
  const [avoidAppear, setAvoidAppear] = useState(false);
  const [goal, setGoal] = useState(5000);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      city,
      skills: skills.split(",").map(s => s.trim()).filter(Boolean),
      available_time: time,
      risk_preference: risk,
      avoid_appearing: avoidAppear,
      monthly_goal: goal,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* City and Goal Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-base font-medium text-gray-700 mb-2">所在城市</label>
          <select
            value={city}
            onChange={e => setCity(e.target.value)}
            disabled={disabled}
            className="w-full px-4 py-3.5 text-lg border-2 border-gray-200 rounded-xl focus:border-purple-400 focus:ring-0 bg-white transition-colors"
          >
            {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-base font-medium text-gray-700 mb-2">月收入目标</label>
          <div className="relative">
            <input
              type="number"
              value={goal}
              onChange={e => setGoal(Number(e.target.value))}
              disabled={disabled}
              min="1000"
              max="100000"
              className="w-full px-4 py-3.5 text-lg border-2 border-gray-200 rounded-xl focus:border-purple-400 focus:ring-0 transition-colors"
            />
            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400">元/月</span>
          </div>
        </div>
      </div>

      {/* Skills */}
      <div>
        <label className="block text-base font-medium text-gray-700 mb-2">
          拥有技能 <span className="text-gray-400 text-sm">(用逗号分隔)</span>
        </label>
        <input
          type="text"
          value={skills}
          onChange={e => setSkills(e.target.value)}
          disabled={disabled}
          placeholder="如: Python, Excel, 剪辑, 设计, 写作"
          className="w-full px-4 py-3.5 text-lg border-2 border-gray-200 rounded-xl focus:border-purple-400 focus:ring-0 transition-colors"
        />
        <p className="text-sm text-gray-500 mt-2">描述您的技能，我们将为您匹配合适的副业</p>
      </div>

      {/* Time and Risk Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-base font-medium text-gray-700 mb-2">每天可用时间</label>
          <select
            value={time}
            onChange={e => setTime(e.target.value)}
            disabled={disabled}
            className="w-full px-4 py-3.5 text-lg border-2 border-gray-200 rounded-xl focus:border-purple-400 focus:ring-0 bg-white transition-colors"
          >
            {TIME_OPTIONS.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-base font-medium text-gray-700 mb-2">风险偏好</label>
          <select
            value={risk}
            onChange={e => setRisk(e.target.value)}
            disabled={disabled}
            className="w-full px-4 py-3.5 text-lg border-2 border-gray-200 rounded-xl focus:border-purple-400 focus:ring-0 bg-white transition-colors"
          >
            {RISK_OPTIONS.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
      </div>

      {/* Avoid Appear Checkbox */}
      <div className="flex items-center p-4 bg-gray-50 rounded-xl">
        <input
          type="checkbox"
          id="avoidAppear"
          checked={avoidAppear}
          onChange={e => setAvoidAppear(e.target.checked)}
          disabled={disabled}
          className="w-5 h-5 text-purple-600 border-2 border-gray-300 rounded focus:ring-purple-500"
        />
        <label htmlFor="avoidAppear" className="ml-3 text-base text-gray-700">
          我不想露脸（选择不需要抛头露面的副业）
        </label>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={disabled}
        className="w-full py-4 px-6 text-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold rounded-xl shadow-lg hover:from-purple-700 hover:to-indigo-700 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {disabled ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            分析中...
          </span>
        ) : (
          "🚀 获取推荐"
        )}
      </button>
    </form>
  );
}