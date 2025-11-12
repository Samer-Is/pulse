"use client";

import { useState } from "react";
import { Wand2, Download, Loader2, Settings2 } from "lucide-react";
import Image from "next/image";

interface GeneratedImage {
  url: string;
  s3_key: string;
  size: string;
  seed?: number;
}

interface ImageResponse {
  job_id: string;
  images: GeneratedImage[];
  provider: string;
  model: string;
  prompt: string;
  count: number;
}

export default function ImagesPage() {
  const [prompt, setPrompt] = useState("");
  const [negativePrompt, setNegativePrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImages, setGeneratedImages] = useState<GeneratedImage[]>([]);
  const [currentJobId, setCurrentJobId] = useState<string>("");
  const [showSettings, setShowSettings] = useState(false);
  
  // Settings
  const [imageCount, setImageCount] = useState(1);
  const [size, setSize] = useState("1024x1024");
  const [seed, setSeed] = useState<string>("");
  const [guidanceScale, setGuidanceScale] = useState(7.5);

  const handleGenerate = async () => {
    if (!prompt.trim() || isGenerating) return;

    setIsGenerating(true);
    setGeneratedImages([]);
    setCurrentJobId("");

    try {
      const response = await fetch("http://localhost:8000/api/v1/images/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Add auth header when authentication is implemented
          // "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          negative_prompt: negativePrompt.trim() || undefined,
          provider: "google",
          count: imageCount,
          size,
          seed: seed ? parseInt(seed) : undefined,
          guidance_scale: guidanceScale,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Image generation failed");
      }

      const data: ImageResponse = await response.json();
      setGeneratedImages(data.images);
      setCurrentJobId(data.job_id);
    } catch (error: any) {
      console.error("Image generation error:", error);
      alert(`Error: ${error.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = async (url: string, index: number) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = `pulse-image-${currentJobId}-${index}.png`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(downloadUrl);
      document.body.removeChild(a);
    } catch (error) {
      console.error("Download failed:", error);
      alert("Failed to download image");
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Pulse Images</h1>
            <p className="text-sm text-gray-500">AI-powered image generation</p>
          </div>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <Settings2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="bg-white border-b px-6 py-4">
          <div className="max-w-7xl mx-auto space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Image Count */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Images: {imageCount}
                </label>
                <input
                  type="range"
                  min="1"
                  max="4"
                  step="1"
                  value={imageCount}
                  onChange={(e) => setImageCount(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              {/* Size */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Image Size
                </label>
                <select
                  value={size}
                  onChange={(e) => setSize(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="256x256">256 × 256 (Small)</option>
                  <option value="512x512">512 × 512 (Medium)</option>
                  <option value="1024x1024">1024 × 1024 (Large)</option>
                  <option value="768x1024">768 × 1024 (Portrait)</option>
                  <option value="1024x768">1024 × 768 (Landscape)</option>
                </select>
              </div>

              {/* Guidance Scale */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Guidance Scale: {guidanceScale.toFixed(1)}
                </label>
                <input
                  type="range"
                  min="1"
                  max="20"
                  step="0.5"
                  value={guidanceScale}
                  onChange={(e) => setGuidanceScale(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Negative Prompt */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Negative Prompt (optional)
                </label>
                <input
                  type="text"
                  value={negativePrompt}
                  onChange={(e) => setNegativePrompt(e.target.value)}
                  placeholder="What to avoid in the image..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Seed */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Seed (optional)
                </label>
                <input
                  type="number"
                  value={seed}
                  onChange={(e) => setSeed(e.target.value)}
                  placeholder="Random seed for reproducibility"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto px-6 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Prompt Input */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Describe the image you want to create
            </label>
            <div className="flex space-x-4">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="A serene landscape with mountains at sunset, digital art style..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                rows={4}
                disabled={isGenerating}
              />
            </div>
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !prompt.trim()}
              className="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center space-x-2"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Wand2 className="w-5 h-5" />
                  <span>Generate Images</span>
                </>
              )}
            </button>
          </div>

          {/* Generated Images Grid */}
          {generatedImages.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Generated Images</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {generatedImages.map((image, index) => (
                  <div
                    key={index}
                    className="bg-white rounded-lg shadow-sm overflow-hidden"
                  >
                    <div className="relative aspect-square">
                      <img
                        src={image.url}
                        alt={`Generated image ${index + 1}`}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="p-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm text-gray-500">
                          Size: {image.size}
                        </span>
                        {image.seed && (
                          <span className="text-sm text-gray-500">
                            Seed: {image.seed}
                          </span>
                        )}
                      </div>
                      <button
                        onClick={() => handleDownload(image.url, index)}
                        className="w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition flex items-center justify-center space-x-2"
                      >
                        <Download className="w-4 h-4" />
                        <span>Download</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Empty State */}
          {generatedImages.length === 0 && !isGenerating && (
            <div className="text-center text-gray-500 mt-12">
              <Wand2 className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <p className="text-lg font-medium">No images generated yet</p>
              <p className="text-sm mt-2">
                Enter a prompt above and click "Generate Images" to create AI art
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

