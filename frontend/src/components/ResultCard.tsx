interface Props {
  data: {
    user_profile: any;
    recommendations: any[];
    selected_recommendation: any;
    action_plan: any;
    validation_result: any;
  };
}

export default function ResultCard({ data }: Props) {
  const { user_profile, recommendations, selected_recommendation, action_plan, validation_result } = data;
  const hustle = selected_recommendation.side_hustle;
  const matchPercent = Math.round(selected_recommendation.match_score * 100);

  return (
    <div className="space-y-6">
      {/* User Profile Summary */}
      <div className="bg-white rounded-2xl p-6 shadow-xl">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-2xl">👤</span>
          <h3 className="text-xl font-semibold text-gray-800">您的画像</h3>
        </div>
        <div className="flex flex-wrap gap-2 mb-4">
          {user_profile.tags.map((tag: string) => (
            <span key={tag} className="px-3 py-1.5 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
              {tag}
            </span>
          ))}
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-gray-500">所在城市</div>
            <div className="font-semibold text-gray-800">{user_profile.city}</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-gray-500">拥有技能</div>
            <div className="font-semibold text-gray-800">{user_profile.skills.length > 0 ? user_profile.skills.join(", ") : "无特殊技能"}</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-gray-500">可用时间</div>
            <div className="font-semibold text-gray-800">每天 {user_profile.available_hours_per_day}h</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-gray-500">月收入目标</div>
            <div className="font-semibold text-gray-800">{user_profile.monthly_goal} 元</div>
          </div>
        </div>
      </div>

      {/* Recommendation - Main Card */}
      <div className="bg-white rounded-2xl p-8 shadow-xl">
        <div className="flex items-start justify-between mb-6">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-3xl">🎯</span>
              <h3 className="text-3xl font-bold text-gray-900">{hustle.name}</h3>
            </div>
            <p className="text-gray-600 text-lg leading-relaxed">{hustle.description}</p>
          </div>
          <div className="ml-6 text-center">
            <div className="relative w-24 h-24">
              <svg className="w-24 h-24 transform -rotate-90">
                <circle cx="48" cy="48" r="40" fill="none" stroke="#e5e7eb" strokeWidth="8" />
                <circle
                  cx="48"
                  cy="48"
                  r="40"
                  fill="none"
                  stroke={matchPercent > 70 ? "#22c55e" : matchPercent > 50 ? "#f59e0b" : "#ef4444"}
                  strokeWidth="8"
                  strokeLinecap="round"
                  strokeDasharray={`${matchPercent * 2.51} 251`}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-2xl font-bold text-gray-800">{matchPercent}%</span>
              </div>
            </div>
            <div className="text-sm text-gray-500 mt-1">匹配度</div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-blue-600">{hustle.startup_cost}元</div>
            <div className="text-sm text-blue-500 mt-1">启动成本</div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-green-600">{hustle.income_potential}元</div>
            <div className="text-sm text-green-500 mt-1">月收入潜力</div>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-purple-600">{hustle.stability}/5</div>
            <div className="text-sm text-purple-500 mt-1">稳定指数</div>
          </div>
        </div>

        {/* Match Reasons */}
        {selected_recommendation.match_reasons.length > 0 && (
          <div className="mb-6">
            <h4 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <span className="text-xl">💡</span> 为什么推荐这个？
            </h4>
            <div className="space-y-2">
              {selected_recommendation.match_reasons.map((reason: string, i: number) => (
                <div key={i} className="flex items-start gap-2 p-3 bg-green-50 rounded-lg">
                  <span className="text-green-500 font-bold">✓</span>
                  <span className="text-gray-700">{reason}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Local Policy Boost */}
        {selected_recommendation.local_policy_boost.length > 0 && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 mb-6">
            <h4 className="font-semibold text-blue-800 mb-2 flex items-center gap-2">
              <span className="text-xl">🏛️</span> 政策加成
            </h4>
            <div className="space-y-1">
              {selected_recommendation.local_policy_boost.map((boost: string, i: number) => (
                <div key={i} className="text-blue-700">✨ {boost}</div>
              ))}
            </div>
          </div>
        )}

        {/* Platform Rules */}
        {hustle.platform_rules.length > 0 && (
          <div className="bg-gray-50 rounded-xl p-4">
            <h4 className="font-semibold text-gray-700 mb-2">📋 平台规则要点</h4>
            <ul className="space-y-1">
              {hustle.platform_rules.map((rule: string, i: number) => (
                <li key={i} className="text-gray-600 text-sm">• {rule}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* All Recommendations */}
      {recommendations.length > 1 && (
        <div className="bg-white rounded-2xl p-6 shadow-xl">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">🔥 其他推荐</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.slice(1).map((rec, idx) => (
              <div key={idx} className="border border-gray-200 rounded-xl p-4 hover:border-purple-300 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-semibold text-gray-800">{rec.side_hustle.name}</h4>
                  <span className="text-sm font-medium text-purple-600">{Math.round(rec.match_score * 100)}%</span>
                </div>
                <p className="text-gray-600 text-sm line-clamp-2">{rec.side_hustle.description}</p>
                <div className="mt-2 flex gap-2 text-xs">
                  <span className="px-2 py-1 bg-gray-100 rounded">启动 {rec.side_hustle.startup_cost}元</span>
                  <span className="px-2 py-1 bg-gray-100 rounded">潜力 {rec.side_hustle.income_potential}元/月</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Plan */}
      <div className="bg-white rounded-2xl p-8 shadow-xl">
        <h3 className="text-xl font-semibold text-gray-800 mb-6 flex items-center gap-2">
          <span className="text-2xl">📅</span> 7日启动计划
        </h3>
        <div className="space-y-4">
          {action_plan.day_plans.map((day: any) => (
            <div key={day.day} className="flex gap-5 p-5 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl">
              <div className="w-14 h-14 flex items-center justify-center bg-gradient-to-br from-purple-600 to-indigo-600 text-white rounded-full text-xl font-bold flex-shrink-0 shadow-lg">
                {day.day}
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-lg text-gray-800 mb-2">{day.title}</h4>
                <ul className="space-y-1">
                  {day.tasks.map((task: string, i: number) => (
                    <li key={i} className="text-gray-600 flex items-start gap-2">
                      <span className="text-purple-400">•</span>
                      <span>{task}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>

        {/* Success Metrics */}
        {action_plan.success_metrics.length > 0 && (
          <div className="mt-6 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-5">
            <h4 className="font-semibold text-green-800 mb-3 flex items-center gap-2">
              <span className="text-xl">🎯</span> 成功指标
            </h4>
            <div className="space-y-2">
              {action_plan.success_metrics.map((metric: string, i: number) => (
                <div key={i} className="text-green-700 flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  {metric}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tips */}
        {action_plan.tips.length > 0 && (
          <div className="mt-4 bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl p-5">
            <h4 className="font-semibold text-purple-800 mb-3 flex items-center gap-2">
              <span className="text-xl">💡</span> 温馨提示
            </h4>
            <div className="space-y-2">
              {action_plan.tips.map((tip: string, i: number) => (
                <div key={i} className="text-purple-700 flex items-center gap-2">
                  <span className="w-2 h-2 bg-purple-400 rounded-full"></span>
                  {tip}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Fallback Options */}
        {action_plan.fallback_options.length > 0 && (
          <div className="mt-4 bg-amber-50 border border-amber-200 rounded-xl p-5">
            <h4 className="font-semibold text-amber-800 mb-3 flex items-center gap-2">
              <span className="text-xl">🔄</span> 备选方案
            </h4>
            <p className="text-amber-700 text-sm">如果这个方案不可行，可以尝试：</p>
            <div className="mt-2 space-y-1">
              {action_plan.fallback_options.map((option: string, i: number) => (
                <div key={i} className="text-amber-700 text-sm">→ {option}</div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Warnings */}
      {validation_result.warnings.length > 0 && (
        <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-xl p-5">
          <h4 className="font-semibold text-yellow-800 mb-3 flex items-center gap-2">
            <span className="text-xl">⚠️</span> 注意事项
          </h4>
          <div className="space-y-2">
            {validation_result.warnings.map((w: string, i: number) => (
              <div key={i} className="text-yellow-700 flex items-start gap-2">
                <span>•</span>
                <span>{w}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}