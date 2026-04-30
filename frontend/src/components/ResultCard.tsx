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
  const incomeRange = user_profile.income_realistic_range || {};

  return (
    <div className="space-y-8">
      {/* ============ User Profile ============ */}
      <div className="bg-[#1a1a3e]/95 backdrop-blur-sm border border-white/[0.08] rounded-3xl p-10 shadow-2xl">
        <div className="flex items-center gap-4 mb-8">
          <span className="text-4xl">👤</span>
          <h3 className="text-3xl font-bold text-white">深度画像分析</h3>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-3 mb-8">
          {user_profile.tags?.map((tag: string) => (
            <span key={tag} className="px-4 py-2 bg-purple-500/20 text-purple-400 rounded-full text-base font-medium">
              {tag}
            </span>
          ))}
        </div>

        {/* Core Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-5 mb-8">
          {[
            { label: "所在城市", value: user_profile.city, sub: user_profile.city_tier },
            { label: "拥有技能", value: user_profile.skills?.length > 0 ? user_profile.skills.join(", ") : "无特殊技能", sub: "" },
            { label: "可用时间", value: user_profile.available_hours_per_day ? `每天 ${user_profile.available_hours_per_day}h` : user_profile.available_time || "—", sub: "" },
            { label: "月收入目标", value: `${user_profile.monthly_goal} 元`, sub: "" },
          ].map(item => (
            <div key={item.label} className="bg-white/10 rounded-2xl p-5">
              <div className="text-white/50 text-sm mb-1">{item.label}</div>
              <div className="font-semibold text-white text-base">{item.value}</div>
              {item.sub && <div className="text-white/40 text-xs mt-0.5">{item.sub}</div>}
            </div>
          ))}
        </div>

        {/* Enhanced Profile Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 收入预期 */}
          {incomeRange.conservative && (
            <div className="bg-green-500/10 border border-green-500/30 rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">💰</span>
                <h4 className="font-bold text-green-400 text-lg">现实收入预期</h4>
              </div>
              <div className="space-y-2">
                {[
                  { label: "保守估计", value: incomeRange.conservative, color: "text-red-600" },
                  { label: "中性估计", value: incomeRange.moderate || incomeRange.neutral || incomeRange.conservative, color: "text-yellow-600" },
                  { label: "乐观估计", value: incomeRange.optimistic || incomeRange.moderate || incomeRange.conservative, color: "text-green-600" },
                ].map(item => (
                  <div key={item.label} className="flex justify-between items-center">
                    <span className="text-green-400">{item.label}</span>
                    <span className={`font-bold text-lg ${item.color}`}>{item.value}元/月</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 技能转化 */}
          {user_profile.transferable_skills?.length > 0 && (
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">🔄</span>
                <h4 className="font-bold text-blue-400 text-xl">可转化技能</h4>
              </div>
              <div className="flex flex-wrap gap-2">
                {user_profile.transferable_skills.map((skill: string) => (
                  <span key={skill} className="px-3 py-1.5 bg-blue-500/20 text-blue-400 rounded-full text-sm font-medium">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* 风险因素 */}
          {user_profile.risk_factors?.length > 0 && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">⚠️</span>
                <h4 className="font-bold text-red-400 text-xl">风险预警</h4>
              </div>
              <ul className="space-y-2">
                {user_profile.risk_factors.map((r: string, i: number) => (
                  <li key={i} className="text-red-400 text-base flex items-start gap-2">
                    <span className="font-bold">•</span>{r}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* 推荐时间线 */}
          {user_profile.recommended_timeline && (
            <div className="bg-purple-500/10 border border-purple-500/30 rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">📅</span>
                <h4 className="font-bold text-purple-400 text-xl">启动建议</h4>
              </div>
              <p className="text-purple-400 text-base leading-relaxed">{user_profile.recommended_timeline}</p>
            </div>
          )}
        </div>
      </div>

      {/* ============ All Recommendations Comparison ============ */}
      {recommendations.length > 1 && (
        <div className="bg-[#1a1a3e]/95 backdrop-blur-sm border border-white/[0.08] rounded-3xl p-10 shadow-2xl">
          <h3 className="text-2xl font-bold text-white mb-8 flex items-center gap-3">
            <span className="text-3xl">🏆</span> 推荐对比
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {recommendations.map((rec: any, idx: number) => {
              const score = Math.round(rec.match_score * 100);
              const isSelected = idx === 0;
              return (
                <div
                  key={idx}
                  className={`rounded-2xl p-6 border-2 transition-all ${isSelected ? "border-purple-500 bg-purple-500/10 shadow-lg" : "border-gray-200 bg-white/10 hover:border-purple-300"}`}
                >
                  {isSelected && (
                    <div className="text-purple-600 text-xs font-bold uppercase tracking-wider mb-2">最佳推荐</div>
                  )}
                  <div className="text-2xl font-bold text-white mb-2">{rec.side_hustle.name}</div>
                  <div className="text-white/70 text-sm mb-4 leading-relaxed">{rec.side_hustle.description?.slice(0, 60)}...</div>
                  <div className="flex items-center justify-between mb-3">
                    <span className={`text-3xl font-bold ${isSelected ? "text-purple-600" : "text-white/80"}`}>{score}%</span>
                    <div className="text-right">
                      <div className="text-xs text-white/50">启动成本</div>
                      <div className="font-bold text-white">{rec.side_hustle.startup_cost}元</div>
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    {rec.match_reasons?.slice(0, 2).map((reason: string, i: number) => (
                      <div key={i} className="text-xs text-white/70 flex items-start gap-1">
                        <span className="text-green-500 shrink-0">✓</span>
                        <span>{reason.slice(0, 50)}{reason.length > 50 ? "..." : ""}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ============ Main Recommendation Card ============ */}
      <div className="bg-[#1a1a3e]/95 backdrop-blur-sm border border-white/[0.08] rounded-3xl p-12 shadow-2xl">
        <div className="flex items-start justify-between mb-10">
          <div className="flex-1">
            <div className="flex items-center gap-5 mb-4">
              <span className="text-5xl">🎯</span>
              <h3 className="text-5xl font-bold text-white">{hustle.name}</h3>
            </div>
            <p className="text-white/70 text-2xl leading-relaxed mt-4 max-w-3xl">{hustle.description}</p>
          </div>
          <div className="ml-10 text-center shrink-0">
            <div className="relative w-32 h-32">
              <svg className="w-32 h-32 transform -rotate-90">
                <circle cx="64" cy="64" r="54" fill="none" stroke="#f1f5f9" strokeWidth="12" />
                <circle
                  cx="64" cy="64" r="54"
                  fill="none"
                  stroke={matchPercent > 70 ? "#22c55e" : matchPercent > 50 ? "#f59e0b" : "#ef4444"}
                  strokeWidth="12"
                  strokeLinecap="round"
                  strokeDasharray={`${matchPercent * 3.39} 339`}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-4xl font-bold text-white">{matchPercent}%</span>
              </div>
            </div>
            <div className="text-base text-white/50 mt-3 font-medium">匹配度</div>
          </div>
        </div>

        {/* 三大指标 */}
        <div className="grid grid-cols-3 gap-6 mb-10">
          {[
            { emoji: "💸", label: "启动成本", value: `${hustle.startup_cost}元`, sub: "初期投入", color: "from-blue-50 to-blue-100", textColor: "text-blue-600" },
            { emoji: "📈", label: "月收入潜力", value: `${hustle.income_potential}元`, sub: "上限参考", color: "from-green-50 to-green-100", textColor: "text-green-600" },
            { emoji: "⭐", label: "稳定指数", value: `${hustle.stability}/5`, sub: "波动风险", color: "from-purple-50 to-purple-100", textColor: "text-purple-600" },
          ].map(item => (
            <div key={item.label} className={`bg-gradient-to-br ${item.color} rounded-2xl p-8 text-center`}>
              <div className="text-4xl mb-3">{item.emoji}</div>
              <div className={`text-4xl font-bold ${item.textColor}`}>{item.value}</div>
              <div className="text-white/50 text-sm mt-2">{item.label}</div>
              <div className="text-white/40 text-xs">{item.sub}</div>
            </div>
          ))}
        </div>

        {/* Match Reasons */}
        {selected_recommendation.match_reasons?.length > 0 && (
          <div className="mb-10">
            <h4 className="font-bold text-white text-2xl mb-6 flex items-center gap-3">
              <span className="text-3xl">💡</span> 为什么推荐这个？
            </h4>
            <div className="space-y-4">
              {selected_recommendation.match_reasons.map((reason: string, i: number) => (
                <div key={i} className="flex items-start gap-4 p-5 bg-green-500/10 rounded-2xl">
                  <span className="text-green-500 font-bold text-2xl shrink-0">✓</span>
                  <span className="text-white/80 text-xl leading-relaxed">{reason}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Policy Boost */}
        {selected_recommendation.local_policy_boost?.length > 0 && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-2xl p-8 mb-10">
            <h4 className="font-bold text-blue-400 text-2xl mb-5 flex items-center gap-3">
              <span className="text-3xl">🏛️</span> 政策加成
            </h4>
            <div className="space-y-3">
              {selected_recommendation.local_policy_boost.map((boost: string, i: number) => (
                <div key={i} className="text-blue-400 text-xl flex items-start gap-2">
                  <span>✨</span><span>{boost}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Platform Rules */}
        {hustle.platform_rules?.length > 0 && (
          <div className="bg-white/10 rounded-2xl p-8 mb-10">
            <h4 className="font-bold text-white text-2xl mb-5">📋 平台规则要点</h4>
            <ul className="space-y-3">
              {hustle.platform_rules.map((rule: string, i: number) => (
                <li key={i} className="text-white/70 text-lg flex items-start gap-2">
                  <span className="text-purple-400 font-bold">•</span><span>{rule}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* ============ Action Plan ============ */}
      <div className="bg-[#1a1a3e]/95 backdrop-blur-sm border border-white/[0.08] rounded-3xl p-12 shadow-2xl">
        <h3 className="text-3xl font-bold text-white mb-10 flex items-center gap-4">
          <span className="text-4xl">📅</span> 7日极速启动计划
        </h3>
        <div className="space-y-6">
          {action_plan.day_plans.map((day: any) => (
            <div key={day.day} className="flex gap-8 p-8 bg-white/8 border border-white/10 rounded-2xl">
              <div className="w-20 h-20 flex items-center justify-center bg-gradient-to-br from-purple-600 to-indigo-600 text-white rounded-2xl text-3xl font-bold shrink-0 shadow-lg">
                D{day.day}
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-2xl text-white mb-4">{day.title}</h4>
                <ul className="space-y-2.5">
                  {day.tasks.map((task: string, i: number) => (
                    <li key={i} className="text-white/70 text-lg flex items-start gap-3">
                      <span className="text-purple-400 font-bold text-xl shrink-0">•</span>
                      <span>{task}</span>
                    </li>
                  ))}
                </ul>
                {day.ai_prompts && Object.keys(day.ai_prompts).length > 0 && (
                  <div className="mt-4 flex flex-wrap gap-2">
                    {Object.entries(day.ai_prompts).map(([name, _]) => (
                      <span key={name} className="px-3 py-1.5 bg-purple-500/20 text-purple-600 rounded-lg text-sm font-medium">
                        🤖 {name}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Success Metrics */}
        {action_plan.success_metrics?.length > 0 && (
          <div className="mt-10 bg-green-500/10 border border-green-500/30 rounded-2xl p-8">
            <h4 className="font-bold text-green-400 text-2xl mb-6 flex items-center gap-3">
              <span className="text-3xl">🎯</span> 成功指标
            </h4>
            <div className="space-y-3">
              {action_plan.success_metrics.map((metric: string, i: number) => (
                <div key={i} className="text-green-400 text-lg flex items-center gap-3">
                  <span className="w-3 h-3 bg-green-400 rounded-full shrink-0"></span>{metric}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tips */}
        {action_plan.tips?.length > 0 && (
          <div className="mt-6 bg-purple-500/10 border border-purple-500/30 rounded-2xl p-8">
            <h4 className="font-bold text-purple-400 text-2xl mb-6 flex items-center gap-3">
              <span className="text-3xl">💡</span> 温馨提示
            </h4>
            <div className="space-y-3">
              {action_plan.tips.map((tip: string, i: number) => (
                <div key={i} className="text-purple-400 text-lg flex items-start gap-3">
                  <span className="w-3 h-3 bg-purple-400 rounded-full shrink-0 mt-1.5"></span><span>{tip}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Fallback Options */}
        {action_plan.fallback_options?.length > 0 && (
          <div className="mt-6 bg-amber-500/10 border-2 border-amber-200 rounded-2xl p-8">
            <h4 className="font-bold text-amber-400 text-2xl mb-5 flex items-center gap-3">
              <span className="text-3xl">🔄</span> 备选方案
            </h4>
            <p className="text-amber-400 text-lg mb-4">如果主方案不可行，可以尝试：</p>
            <div className="space-y-2">
              {action_plan.fallback_options.map((option: string, i: number) => (
                <div key={i} className="text-amber-400 text-lg">→ {option}</div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ============ Validation Warnings ============ */}
      {validation_result.warnings?.length > 0 && (
        <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-200 rounded-2xl p-8">
          <h4 className="font-bold text-yellow-800 text-2xl mb-6 flex items-center gap-3">
            <span className="text-3xl">⚠️</span> 注意事项
          </h4>
          <div className="space-y-3">
            {validation_result.warnings.map((w: string, i: number) => (
              <div key={i} className="text-yellow-400 text-lg flex items-start gap-2">
                <span className="font-bold">•</span><span>{w}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
