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
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* City */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">所在城市</label>
          <select
            value={city}
            onChange={e => setCity(e.target.value)}
            disabled={disabled}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>

        {/* Goal */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">月收入目标 (元)</label>
          <input
            type="number"
            value={goal}
            onChange={e => setGoal(Number(e.target.value))}
            disabled={disabled}
            min="1000"
            max="100000"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Skills */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">拥有技能 (用逗号分隔)</label>
        <input
          type="text"
          value={skills}
          onChange={e => setSkills(e.target.value)}
          disabled={disabled}
          placeholder="如: Python, Excel, 剪辑"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Time */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">每天可用时间</label>
          <select
            value={time}
            onChange={e => setTime(e.target.value)}
            disabled={disabled}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            {TIME_OPTIONS.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>

        {/* Risk */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">风险偏好</label>
          <select
            value={risk}
            onChange={e => setRisk(e.target.value)}
            disabled={disabled}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            {RISK_OPTIONS.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
      </div>

      {/* Avoid Appear */}
      <div className="flex items-center">
        <input
          type="checkbox"
          id="avoidAppear"
          checked={avoidAppear}
          onChange={e => setAvoidAppear(e.target.checked)}
          disabled={disabled}
          className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
        />
        <label htmlFor="avoidAppear" className="ml-2 text-sm text-gray-700">厌恶露脸</label>
      </div>

      <button
        type="submit"
        disabled={disabled}
        className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold rounded-lg shadow-lg hover:from-purple-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {disabled ? "分析中..." : "获取推荐"}
      </button>
    </form>
  );
}