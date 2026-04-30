import { useState, useEffect, useRef } from "react";

interface Material {
  id: number;
  filename: string;
  file_path: string;
  file_type: string;
  mime_type: string;
  file_size: number;
  width?: number;
  height?: number;
  duration?: number;
  tags: string[];
  folder: string;
  created_at: string;
}

interface Props {
  token: string;
  onBack: () => void;
  onSelect?: (material: Material) => void;
  selectMode?: boolean;
}

export default function MaterialManager({ token, onBack, onSelect, selectMode = false }: Props) {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [filter, setFilter] = useState<"all" | "image" | "video" | "audio">("all");
  const [folder, setFolder] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchMaterials();
  }, [token, filter]);

  const fetchMaterials = async () => {
    try {
      const params = new URLSearchParams();
      if (filter !== "all") params.set("file_type", filter);
      if (folder) params.set("folder", folder);

      const res = await fetch(`/api/materials?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.success) {
        setMaterials(data.materials || []);
      }
    } catch (error) {
      console.error("获取素材失败:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    try {
      for (const file of Array.from(files)) {
        const formData = new FormData();
        formData.append("file", file);
        if (folder) formData.append("folder", folder);

        const res = await fetch("/api/materials/upload", {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: formData,
        });
        const data = await res.json();
        if (!data.success) {
          console.error("上传失败:", data.message);
        }
      }
      fetchMaterials();
    } catch (error) {
      console.error("上传失败:", error);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("确定要删除这个素材吗？")) return;
    try {
      const res = await fetch(`/api/materials/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.success) {
        setMaterials(materials.filter((m) => m.id !== id));
      }
    } catch (error) {
      console.error("删除失败:", error);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const getFileIcon = (mimeType: string) => {
    if (mimeType.startsWith("image/")) return "🖼️";
    if (mimeType.startsWith("video/")) return "🎬";
    if (mimeType.startsWith("audio/")) return "🎵";
    return "📄";
  };

  const isImage = (mimeType: string) => mimeType.startsWith("image/");

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">素材库</h1>
          <p className="text-white/50 text-sm mt-1">管理您的图片、视频和音频素材</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={onBack}
            className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-medium transition-colors"
          >
            返回
          </button>
        </div>
      </div>

      {/* Upload Area */}
      <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-white">上传素材</h3>
          <div className="flex items-center gap-3">
            <input
              type="text"
              placeholder="文件夹路径"
              value={folder}
              onChange={(e) => setFolder(e.target.value)}
              className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-white text-sm"
            />
            <label className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-sm font-medium cursor-pointer transition-colors">
              {uploading ? "上传中..." : "选择文件"}
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,video/*,audio/*"
                onChange={handleUpload}
                className="hidden"
                disabled={uploading}
              />
            </label>
          </div>
        </div>
        <div className="text-white/40 text-sm">
          支持格式：JPG, PNG, GIF, MP4, MP3, WAV 等
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        {(["all", "image", "video", "audio"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
              filter === f
                ? "bg-purple-600 text-white"
                : "bg-white/5 text-white/60 hover:bg-white/10"
            }`}
          >
            {f === "all" ? "全部" : f === "image" ? "图片" : f === "video" ? "视频" : "音频"}
          </button>
        ))}
      </div>

      {/* Materials Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-white/60">加载中...</div>
        </div>
      ) : materials.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 text-white/40">
          <div className="text-6xl mb-4">📁</div>
          <div>暂无素材，上传您的第一个文件吧</div>
        </div>
      ) : (
        <div className="grid grid-cols-4 gap-4">
          {materials.map((m) => (
            <div
              key={m.id}
              className={`bg-white/5 rounded-xl p-3 border border-white/10 hover:border-purple-500/50 transition-colors group ${
                selectMode ? "cursor-pointer" : ""
              }`}
              onClick={() => selectMode && onSelect && onSelect(m)}
            >
              {isImage(m.mime_type) ? (
                <div className="aspect-video bg-black/20 rounded-lg mb-2 overflow-hidden">
                  <img
                    src={m.file_path}
                    alt={m.filename}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = "none";
                    }}
                  />
                </div>
              ) : (
                <div className="aspect-video bg-black/20 rounded-lg mb-2 flex items-center justify-center text-4xl">
                  {getFileIcon(m.mime_type)}
                </div>
              )}
              <div className="space-y-1">
                <div className="text-white text-sm truncate" title={m.filename}>
                  {m.filename}
                </div>
                <div className="flex items-center justify-between text-xs text-white/40">
                  <span>{formatFileSize(m.file_size)}</span>
                  {m.width && m.height && <span>{m.width}x{m.height}</span>}
                </div>
              </div>
              {!selectMode && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(m.id);
                  }}
                  className="mt-2 w-full py-1 bg-red-500/20 hover:bg-red-500/40 text-red-300 rounded-lg text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  删除
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
