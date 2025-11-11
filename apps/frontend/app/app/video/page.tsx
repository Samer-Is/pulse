"use client";

import { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { ModelSelector } from "@/components/ModelSelector";
import { VideoEditor } from "@/components/Editors/VideoEditor";

export default function VideoPage() {
  const [model, setModel] = useState("veo3:default");
  const [prompt, setPrompt] = useState("");
  const [videos, setVideos] = useState<any[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      // TODO: Call gateway API
      // const result = await video.generate({ model, prompt, duration_s: 5 });
      // setVideos([result]);
      
      alert("Video generation coming soon!");
    } catch (error: any) {
      alert(error.message || "Video generation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen">
      <Sidebar locale="ar" />
      <div className="flex-1 overflow-y-auto p-8 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-6">محرر ومولد الفيديو</h1>

          {/* Model Selector */}
          <div className="mb-6">
            <ModelSelector
              value={model}
              onChange={setModel}
              models={[
                { id: "veo3:default", name: "Veo3" },
                { id: "pika:1.0", name: "Pika" },
                { id: "runway:gen-2", name: "Runway Gen-2" },
              ]}
            />
          </div>

          {/* Prompt Input */}
          <div className="mb-6 bg-white rounded-lg shadow p-6">
            <label className="block text-sm font-medium mb-2">
              وصف الفيديو
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="صف الفيديو الذي تريد إنشاءه..."
              rows={3}
              className="w-full px-3 py-2 border rounded"
            />
            <button
              onClick={handleGenerate}
              disabled={loading || !prompt}
              className="mt-4 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "جارٍ الإنشاء..." : "إنشاء الفيديو"}
            </button>

            {loading && (
              <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded">
                <p className="text-sm text-yellow-800">
                  ⏳ معالجة الفيديو قد تستغرق عدة دقائق. سيتم إشعارك عند الانتهاء.
                </p>
              </div>
            )}
          </div>

          {/* Video Grid */}
          {videos.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {videos.map((vid, index) => (
                <div
                  key={index}
                  className="bg-white rounded-lg shadow p-4"
                >
                  <video
                    src={vid.video_url}
                    controls
                    className="w-full rounded"
                  />
                  <button
                    onClick={() => setSelectedVideo(vid.video_url)}
                    className="mt-3 w-full py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                  >
                    تحرير الفيديو
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Video Editor */}
          {selectedVideo && (
            <VideoEditor
              videoUrl={selectedVideo}
              onSave={(url) => {
                alert("Video saved!");
                setSelectedVideo(null);
              }}
              locale="ar"
            />
          )}
        </div>
      </div>
    </div>
  );
}

