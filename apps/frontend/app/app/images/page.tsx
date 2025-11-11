"use client";

import { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { ModelSelector } from "@/components/ModelSelector";
import { ImageEditor } from "@/components/Editors/ImageEditor";

export default function ImagesPage() {
  const [model, setModel] = useState("nano-banana:default");
  const [prompt, setPrompt] = useState("");
  const [images, setImages] = useState<string[]>([]);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      // TODO: Call gateway API
      // const result = await images.generate({ model, prompt, count: 4 });
      // setImages(result.images.map(img => img.url));
      
      alert("Image generation coming soon!");
    } catch (error: any) {
      alert(error.message || "Image generation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen">
      <Sidebar locale="ar" />
      <div className="flex-1 overflow-y-auto p-8 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-6">محرر ومولد الصور</h1>

          {/* Model Selector */}
          <div className="mb-6">
            <ModelSelector
              value={model}
              onChange={setModel}
              models={[
                { id: "nano-banana:default", name: "Nano Banana" },
                { id: "replicate:stable-diffusion-xl", name: "Stable Diffusion XL" },
              ]}
            />
          </div>

          {/* Prompt Input */}
          <div className="mb-6 bg-white rounded-lg shadow p-6">
            <label className="block text-sm font-medium mb-2">
              وصف الصورة
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="صف الصورة التي تريد إنشاءها..."
              rows={3}
              className="w-full px-3 py-2 border rounded"
            />
            <button
              onClick={handleGenerate}
              disabled={loading || !prompt}
              className="mt-4 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "جارٍ الإنشاء..." : "إنشاء الصور"}
            </button>
          </div>

          {/* Image Grid */}
          {images.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              {images.map((img, index) => (
                <div
                  key={index}
                  onClick={() => setSelectedImage(img)}
                  className="cursor-pointer hover:opacity-75 transition"
                >
                  <img
                    src={img}
                    alt={`Generated ${index + 1}`}
                    className="w-full h-48 object-cover rounded-lg border"
                  />
                </div>
              ))}
            </div>
          )}

          {/* Image Editor */}
          {selectedImage && (
            <ImageEditor
              imageUrl={selectedImage}
              onSave={(url) => {
                alert("Image saved!");
                setSelectedImage(null);
              }}
              locale="ar"
            />
          )}
        </div>
      </div>
    </div>
  );
}

