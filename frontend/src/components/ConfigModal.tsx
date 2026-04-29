import { useState, useEffect } from "react";
import { AppConfig, getModels } from "../api";

interface Props {
  config: AppConfig | null;
  onSave: (config: AppConfig) => void;
  onClose: () => void;
}

const PROVIDERS = [
  { id: "deepseek", name: "DeepSeek", default_model: "deepseek-chat" },
  { id: "qwen", name: "阿里云千问", default_model: "qwen-turbo" },
  { id: "kimi", name: "Kimi (Moonshot)", default_model: "moonshot-v1-8k" },
  { id: "minimax", name: "MiniMax", default_model: "MiniMax-Text-01" },
  { id: "openai", name: "OpenAI", default_model: "gpt-4o" },
  { id: "anthropic", name: "Anthropic (Claude)", default_model: "claude-sonnet-4-20250514" },
];

const MODELS: Record<string, string[]> = {
  deepseek: ["deepseek-chat", "deepseek-coder"],
  qwen: ["qwen-turbo", "qwen-plus", "qwen-max"],
  kimi: ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
  minimax: ["MiniMax-Text-01", "abab6.chat"],
  openai: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
  anthropic: ["claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-haiku-4-20250514"],
};

export default function ConfigModal({ config, onSave, onClose }: Props) {
  const [provider, setProvider] = useState(config?.llm_provider || "deepseek");
  const [apiKey, setApiKey] = useState(config?.llm_api_key || "");
  const [model, setModel] = useState(config?.llm_model || "");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!model) {
      const defaultModel = PROVIDERS.find(p => p.id === provider)?.default_model || "";
      setModel(defaultModel);
    }
  }, [provider, model]);

  const handleProviderChange = (newProvider: string) => {
    setProvider(newProvider);
    const defaultModel = PROVIDERS.find(p => p.id === newProvider)?.default_model || "";
    setModel(defaultModel);
  };

  const handleSave = async () => {
    if (!apiKey.trim()) {
      alert("请输入 API Key");
      return;
    }
    setSaving(true);
    try {
      await onSave({ llm_provider: provider, llm_api_key: apiKey, llm_model: model });
    } finally {
      setSaving(false);
    }
  };

  const models = MODELS[provider] || [];

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-800">⚙️ LLM 配置</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5">
          {/* Provider */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">模型提供商</label>
            <div className="grid grid-cols-2 gap-2">
              {PROVIDERS.map(p => (
                <button
                  key={p.id}
                  onClick={() => handleProviderChange(p.id)}
                  className={`py-3 px-4 rounded-xl text-center font-medium transition-all ${
                    provider === p.id
                      ? "bg-purple-600 text-white shadow-md"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  {p.name}
                </button>
              ))}
            </div>
          </div>

          {/* API Key */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">API Key</label>
            <input
              type="password"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
              placeholder="请输入 API Key"
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              您的 API Key 仅保存在本地，不会上传到任何服务器
            </p>
          </div>

          {/* Model */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">模型</label>
            <select
              value={model}
              onChange={e => setModel(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white"
            >
              {models.map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-3 px-4 bg-gray-100 text-gray-700 font-medium rounded-xl hover:bg-gray-200 transition-colors"
          >
            取消
          </button>
          <button
            onClick={handleSave}
            disabled={saving || !apiKey.trim()}
            className="flex-1 py-3 px-4 bg-purple-600 text-white font-medium rounded-xl hover:bg-purple-700 transition-colors disabled:opacity-50"
          >
            {saving ? "保存中..." : "保存"}
          </button>
        </div>
      </div>
    </div>
  );
}