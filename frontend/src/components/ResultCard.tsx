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
  const { user_profile, selected_recommendation, action_plan, validation_result } = data;
  const hustle = selected_recommendation.side_hustle;

  return (
    <div className="space-y-6">
      {/* User Profile Summary */}
      <div className="bg-white rounded-2xl p-6 shadow-xl">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">您的画像</h3>
        <div className="flex flex-wrap gap-3">
          {user_profile.tags.map((tag: string) => (
            <span key={tag} className="px-4 py-2 bg-purple-100 text-purple-700 rounded-full text-base font-medium">
              {tag}
            </span>
          ))}
        </div>
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
          <div><span className="font-medium">城市:</span> {user_profile.city}</div>
          <div><span className="font-medium">技能:</span> {user_profile.skills.join(", ") || "无"}</div>
          <div><span className="font-medium">时间:</span> 每天 {user_profile.available_hours_per_day}h</div>
          <div><span className="font-medium">目标:</span> {user_profile.monthly_goal}元/月</div>
        </div>
      </div>

      {/* Recommendation */}
      <div className="bg-white rounded-2xl p-6 shadow-xl">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">{hustle.name}</h3>
            <p className="text-gray-600 mt-2 text-lg">{hustle.description}</p>
          </div>
          <div className="text-right ml-4">
            <div className="text-4xl font-bold text-green-600">{Math.round(selected_recommendation.match_score * 100)}%</div>
            <div className="text-base text-gray-500">匹配度</div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 bg-gray-50 rounded-xl">
            <div className="text-2xl font-bold text-gray-900">{hustle.startup_cost}元</div>
            <div className="text-base text-gray-500 mt-1">启动成本</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-xl">
            <div className="text-2xl font-bold text-gray-900">{hustle.min_time_hours}h/天</div>
            <div className="text-base text-gray-500 mt-1">时间要求</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-xl">
            <div className="text-2xl font-bold text-green-600">{hustle.income_potential}元</div>
            <div className="text-base text-gray-500 mt-1">月收入潜力</div>
          </div>
        </div>

        {/* Match Reasons */}
        {selected_recommendation.match_reasons.length > 0 && (
          <div className="mb-4">
            <h4 className="font-semibold text-gray-700 mb-3">为什么推荐这个？</h4>
            <ul className="space-y-2">
              {selected_recommendation.match_reasons.map((reason: string, i: number) => (
                <li key={i} className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span className="text-gray-700">{reason}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Local Policy Boost */}
        {selected_recommendation.local_policy_boost.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <h4 className="font-semibold text-blue-800 mb-2">政策加成</h4>
            <ul className="space-y-1 text-blue-700">
              {selected_recommendation.local_policy_boost.map((boost: string, i: number) => (
                <li key={i}>✨ {boost}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Action Plan */}
      <div className="bg-white rounded-2xl p-6 shadow-xl">
        <h3 className="text-xl font-semibold text-gray-800 mb-6">7日启动计划</h3>
        <div className="space-y-4">
          {action_plan.day_plans.map((day: any) => (
            <div key={day.day} className="flex gap-5 p-5 bg-gray-50 rounded-xl">
              <div className="w-14 h-14 flex items-center justify-center bg-gradient-to-br from-purple-600 to-indigo-600 text-white rounded-full text-xl font-bold flex-shrink-0">
                D{day.day}
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-lg text-gray-800 mb-2">{day.title}</h4>
                <ul className="space-y-1">
                  {day.tasks.map((task: string, i: number) => (
                    <li key={i} className="text-gray-600">• {task}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>

        {/* Success Metrics */}
        {action_plan.success_metrics.length > 0 && (
          <div className="mt-6 bg-green-50 border border-green-200 rounded-xl p-4">
            <h4 className="font-semibold text-green-800 mb-2">成功指标</h4>
            <ul className="space-y-1 text-green-700">
              {action_plan.success_metrics.map((metric: string, i: number) => (
                <li key={i}>🎯 {metric}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Tips */}
        {action_plan.tips.length > 0 && (
          <div className="mt-4 bg-purple-50 border border-purple-200 rounded-xl p-4">
            <h4 className="font-semibold text-purple-800 mb-2">温馨提示</h4>
            <ul className="space-y-1 text-purple-700">
              {action_plan.tips.map((tip: string, i: number) => (
                <li key={i}>💡 {tip}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Warnings */}
      {validation_result.warnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-5">
          <h4 className="font-semibold text-yellow-800 mb-2">⚠️ 注意事项</h4>
          <ul className="space-y-1 text-yellow-700">
            {validation_result.warnings.map((w: string, i: number) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}