"use client";

import { useState, useEffect, useRef } from "react";
import { Video, Loader2, Download, CheckCircle, XCircle, Clock } from "lucide-react";

interface VideoJob {
  job_id: string;
  status: string;
  progress?: number;
  video_url?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export default function VideosPage() {
  const [prompt, setPrompt] = useState("");
  const [provider, setProvider] = useState("runway");
  const [duration, setDuration] = useState(4);
  const [style, setStyle] = useState("");
  const [aspectRatio, setAspectRatio] = useState("16:9");
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentJob, setCurrentJob] = useState<VideoJob | null>(null);
  const [generatedVideos, setGeneratedVideos] = useState<VideoJob[]>([]);
  
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // Cleanup EventSource on unmount
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleGenerate = async () => {
    if (!prompt.trim() || isGenerating) return;

    setIsGenerating(true);
    setCurrentJob(null);

    try {
      const response = await fetch("http://localhost:8000/api/v1/videos/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Add auth header when authentication is implemented
          // "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          provider,
          duration,
          style: style || undefined,
          aspect_ratio: aspectRatio,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Video generation failed");
      }

      const data = await response.json();
      
      // Start streaming status updates
      startStatusStream(data.job_id);
    } catch (error: any) {
      console.error("Video generation error:", error);
      alert(`Error: ${error.message}`);
      setIsGenerating(false);
    }
  };

  const startStatusStream = (jobId: string) => {
    // Close existing connection if any
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const eventSource = new EventSource(
      `http://localhost:8000/api/v1/videos/${jobId}/stream`
    );

    eventSource.onmessage = (event) => {
      if (event.data === "[DONE]") {
        eventSource.close();
        setIsGenerating(false);
        
        // Add to generated videos if completed successfully
        if (currentJob?.video_url) {
          setGeneratedVideos(prev => [currentJob, ...prev]);
        }
        return;
      }

      try {
        const jobStatus: VideoJob = JSON.parse(event.data);
        setCurrentJob(jobStatus);

        if (jobStatus.status === "completed" || jobStatus.status === "failed") {
          eventSource.close();
          setIsGenerating(false);
          
          if (jobStatus.status === "completed" && jobStatus.video_url) {
            setGeneratedVideos(prev => [jobStatus, ...prev]);
          }
        }
      } catch (e) {
        console.error("Failed to parse job status:", e);
      }
    };

    eventSource.onerror = (error) => {
      console.error("EventSource error:", error);
      eventSource.close();
      setIsGenerating(false);
    };

    eventSourceRef.current = eventSource;
  };

  const handleDownload = async (url: string, jobId: string) => {
    try {
      const a = document.createElement("a");
      a.href = url;
      a.download = `pulse-video-${jobId}.mp4`;
      a.target = "_blank";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (error) {
      console.error("Download failed:", error);
      alert("Failed to download video");
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "pending":
        return <Clock className="w-5 h-5 text-gray-500" />;
      case "processing":
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "pending":
        return "Queued";
      case "processing":
        return "Generating...";
      case "completed":
        return "Completed";
      case "failed":
        return "Failed";
      default:
        return status;
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900">Pulse Videos</h1>
          <p className="text-sm text-gray-500">AI-powered video generation</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto px-6 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Input Form */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Describe the video you want to create
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="A beautiful sunset over the ocean with waves..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none mb-4"
              rows={4}
              disabled={isGenerating}
            />

            {/* Settings Row */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Provider
                </label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  disabled={isGenerating}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="runway">Runway</option>
                  <option value="pika">Pika</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Duration: {duration}s
                </label>
                <input
                  type="range"
                  min="2"
                  max="10"
                  step="1"
                  value={duration}
                  onChange={(e) => setDuration(parseInt(e.target.value))}
                  disabled={isGenerating}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Aspect Ratio
                </label>
                <select
                  value={aspectRatio}
                  onChange={(e) => setAspectRatio(e.target.value)}
                  disabled={isGenerating}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="16:9">16:9 (Landscape)</option>
                  <option value="9:16">9:16 (Portrait)</option>
                  <option value="1:1">1:1 (Square)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Style (optional)
                </label>
                <input
                  type="text"
                  value={style}
                  onChange={(e) => setStyle(e.target.value)}
                  placeholder="cinematic, anime..."
                  disabled={isGenerating}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating || !prompt.trim()}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center space-x-2"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Video className="w-5 h-5" />
                  <span>Generate Video</span>
                </>
              )}
            </button>
          </div>

          {/* Current Job Progress */}
          {currentJob && (
            <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
              <h2 className="text-lg font-semibold mb-4">Current Generation</h2>
              <div className="flex items-center space-x-4">
                {getStatusIcon(currentJob.status)}
                <div className="flex-1">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium">{getStatusText(currentJob.status)}</span>
                    {currentJob.progress !== undefined && (
                      <span className="text-sm text-gray-500">{currentJob.progress}%</span>
                    )}
                  </div>
                  {currentJob.progress !== undefined && (
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${currentJob.progress}%` }}
                      />
                    </div>
                  )}
                  {currentJob.error_message && (
                    <p className="text-sm text-red-600 mt-2">{currentJob.error_message}</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Generated Videos */}
          {generatedVideos.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Generated Videos</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {generatedVideos.map((video) => (
                  <div key={video.job_id} className="bg-white rounded-lg shadow-sm overflow-hidden">
                    {video.video_url ? (
                      <div className="relative aspect-video bg-gray-900">
                        <video
                          src={video.video_url}
                          controls
                          className="w-full h-full"
                        />
                      </div>
                    ) : (
                      <div className="aspect-video bg-gray-200 flex items-center justify-center">
                        <Video className="w-12 h-12 text-gray-400" />
                      </div>
                    )}
                    <div className="p-4">
                      <div className="flex justify-between items-center mb-2">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(video.status)}
                          <span className="text-sm font-medium">{getStatusText(video.status)}</span>
                        </div>
                        <span className="text-xs text-gray-500">
                          {new Date(video.created_at).toLocaleString()}
                        </span>
                      </div>
                      {video.video_url && (
                        <button
                          onClick={() => handleDownload(video.video_url!, video.job_id)}
                          className="w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition flex items-center justify-center space-x-2"
                        >
                          <Download className="w-4 h-4" />
                          <span>Download</span>
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Empty State */}
          {generatedVideos.length === 0 && !currentJob && (
            <div className="text-center text-gray-500 mt-12">
              <Video className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <p className="text-lg font-medium">No videos generated yet</p>
              <p className="text-sm mt-2">
                Enter a prompt above and click "Generate Video" to create AI videos
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

