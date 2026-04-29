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
    <div className="space-y-4">
      {/* User Profile Summary */}
      <div className="bg-white rounded-xl p-4 shadow">
        <h3 className="font-semibold text-gray-800 mb-2">您的画像</h3>
        <div className="flex flex-wrap gap-2">
          {user_profile.tags.map((tag: string) => (
            <span key={tag} className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-sm">
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Recommendation */}
      <div className="bg-white rounded-xl p-4 shadow">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-xl font-bold text-gray-900">{hustle.name}</h3>
            <p className="text-gray-600 mt-1">{hustle.description}</p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-green-600">{selected_recommendation.match_score * 100}%</div>
            <div className="text-sm text-gray-500">匹配度</div>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-lg font-semibold">{hustle.startup_cost}元</div>
            <div className="text-sm text-gray-500">启动成本</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-lg font-semibold">{hustle.min_time_hours}h/天</div>
            <div className="text-sm text-gray-500">时间要求</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-lg font-semibold">{hustle.income_potential}元</div>
            <div className="text-sm text-gray-500">月收入潜力</div>
          </div>
        </div>

        {/* Match Reasons */}
        {selected_recommendation.match_reasons.length > 0 && (
          <div className="mt-4">
            <h4 className="font-medium text-gray-700 mb-2">匹配原因</h4>
            <ul className="list-disc list-inside text-sm text-gray-600">
              {selected_recommendation.match_reasons.map((reason: string, i: number) => (
                <li key={i}>{reason}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Action Plan */}
      <div className="bg-white rounded-xl p-4 shadow">
        <h3 className="font-semibold text-gray-800 mb-4">7日启动计划</h3>
        <div className="space-y-3">
          {action_plan.day_plans.map((day: any) => (
            <div key={day.day} className="flex gap-4 p-3 bg-gray-50 rounded-lg">
              <div className="w-12 h-12 flex items-center justify-center bg-purple-600 text-white rounded-full font-bold">
                D{day.day}
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-800">{day.title}</h4>
                <ul className="mt-1 text-sm text-gray-600">
                  {day.tasks.map((task: string, i: number) => (
                    <li key={i}>• {task}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Warnings */}
      {validation_result.warnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
          <h4 className="font-medium text-yellow-800 mb-2">注意事项</h4>
          <ul className="list-disc list-inside text-sm text-yellow-700">
            {validation_result.warnings.map((w: string, i: number) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}