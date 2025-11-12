"use client";

import { useState } from "react";
import { Presentation, Download, Sparkles, Plus, Trash2, Loader2 } from "lucide-react";

interface SlideContent {
  title: string;
  content: string[];
}

type Mode = "auto" | "manual";

export default function SlidesPage() {
  const [mode, setMode] = useState<Mode>("auto");
  
  // Auto-generate mode
  const [topic, setTopic] = useState("");
  const [numSlides, setNumSlides] = useState(5);
  const [audience, setAudience] = useState("");
  const [style, setStyle] = useState("");
  
  // Manual mode
  const [manualTopic, setManualTopic] = useState("");
  const [slides, setSlides] = useState<SlideContent[]>([
    { title: "", content: [""] },
  ]);
  
  // Common
  const [format, setFormat] = useState<"pptx" | "pdf">("pptx");
  const [isGeneratingOutline, setIsGeneratingOutline] = useState(false);
  const [isGeneratingSlides, setIsGeneratingSlides] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string>("");
  const [generatedSlideCount, setGeneratedSlideCount] = useState(0);

  const handleGenerateOutline = async () => {
    if (!topic.trim()) {
      alert("Please enter a topic");
      return;
    }

    setIsGeneratingOutline(true);

    try {
      const response = await fetch("http://localhost:8000/api/v1/slides/generate-outline", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Add auth header when authentication is implemented
        },
        body: JSON.stringify({
          topic,
          num_slides: numSlides,
          audience: audience || undefined,
          style: style || undefined,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Outline generation failed");
      }

      const data = await response.json();
      
      // Switch to manual mode and populate slides
      setMode("manual");
      setManualTopic(data.topic);
      setSlides(data.slides);
      
      alert("Outline generated! You can now edit it or generate directly.");
    } catch (error: any) {
      console.error("Outline generation error:", error);
      alert(`Error: ${error.message}`);
    } finally {
      setIsGeneratingOutline(false);
    }
  };

  const handleGenerateSlides = async () => {
    setIsGeneratingSlides(true);
    setDownloadUrl("");

    try {
      let requestBody: any = { format };

      if (mode === "auto") {
        if (!topic.trim()) {
          alert("Please enter a topic");
          return;
        }
        requestBody = {
          ...requestBody,
          topic,
          auto_generate: true,
          num_slides: numSlides,
        };
      } else {
        // Manual mode - validate slides
        const validSlides = slides.filter((s) => s.title.trim() && s.content.some((c) => c.trim()));
        
        if (validSlides.length === 0) {
          alert("Please add at least one slide with a title and content");
          return;
        }

        requestBody = {
          ...requestBody,
          topic: manualTopic || "Presentation",
          auto_generate: false,
          outline: validSlides.map((s) => ({
            title: s.title,
            content: s.content.filter((c) => c.trim()),
          })),
        };
      }

      const response = await fetch("http://localhost:8000/api/v1/slides/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Add auth header when authentication is implemented
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Slide generation failed");
      }

      const data = await response.json();
      setDownloadUrl(data.download_url);
      setGeneratedSlideCount(data.slide_count);
    } catch (error: any) {
      console.error("Slide generation error:", error);
      alert(`Error: ${error.message}`);
    } finally {
      setIsGeneratingSlides(false);
    }
  };

  const addSlide = () => {
    setSlides([...slides, { title: "", content: [""] }]);
  };

  const removeSlide = (index: number) => {
    if (slides.length > 1) {
      setSlides(slides.filter((_, i) => i !== index));
    }
  };

  const updateSlideTitle = (index: number, title: string) => {
    const newSlides = [...slides];
    newSlides[index].title = title;
    setSlides(newSlides);
  };

  const updateBulletPoint = (slideIndex: number, bulletIndex: number, value: string) => {
    const newSlides = [...slides];
    newSlides[slideIndex].content[bulletIndex] = value;
    setSlides(newSlides);
  };

  const addBulletPoint = (slideIndex: number) => {
    const newSlides = [...slides];
    newSlides[slideIndex].content.push("");
    setSlides(newSlides);
  };

  const removeBulletPoint = (slideIndex: number, bulletIndex: number) => {
    const newSlides = [...slides];
    if (newSlides[slideIndex].content.length > 1) {
      newSlides[slideIndex].content = newSlides[slideIndex].content.filter(
        (_, i) => i !== bulletIndex
      );
      setSlides(newSlides);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Slide Maker</h1>
          <p className="text-gray-600">
            Create professional presentations with AI assistance
          </p>
        </div>

        {/* Mode Selection */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Choose Mode</h2>
          <div className="flex space-x-4">
            <button
              onClick={() => setMode("auto")}
              className={`flex-1 py-3 px-4 rounded-lg border-2 transition ${
                mode === "auto"
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-300 hover:border-gray-400"
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <Sparkles className="w-5 h-5" />
                <span className="font-medium">AI Generate</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">Let AI create slides from a topic</p>
            </button>
            <button
              onClick={() => setMode("manual")}
              className={`flex-1 py-3 px-4 rounded-lg border-2 transition ${
                mode === "manual"
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-300 hover:border-gray-400"
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <Presentation className="w-5 h-5" />
                <span className="font-medium">Manual Entry</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">Create slides yourself</p>
            </button>
          </div>
        </div>

        {/* AI Generate Mode */}
        {mode === "auto" && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">AI Generation</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Topic *
                </label>
                <input
                  type="text"
                  placeholder="e.g., Introduction to Machine Learning"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Number of Slides
                  </label>
                  <input
                    type="number"
                    min="3"
                    max="20"
                    value={numSlides}
                    onChange={(e) => setNumSlides(parseInt(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Audience (Optional)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., Beginners"
                    value={audience}
                    onChange={(e) => setAudience(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Style (Optional)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., Technical"
                    value={style}
                    onChange={(e) => setStyle(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <button
                onClick={handleGenerateOutline}
                disabled={isGeneratingOutline}
                className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center space-x-2"
              >
                {isGeneratingOutline ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Generating Outline...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Generate Outline (Preview)</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Manual Entry Mode */}
        {mode === "manual" && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Manual Slide Entry</h2>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Presentation Title
              </label>
              <input
                type="text"
                placeholder="e.g., My Presentation"
                value={manualTopic}
                onChange={(e) => setManualTopic(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Slides */}
            <div className="space-y-4">
              {slides.map((slide, slideIdx) => (
                <div key={slideIdx} className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-lg font-semibold text-gray-700">
                      Slide {slideIdx + 1}
                    </h3>
                    {slides.length > 1 && (
                      <button
                        onClick={() => removeSlide(slideIdx)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                  <input
                    type="text"
                    placeholder="Slide Title"
                    value={slide.title}
                    onChange={(e) => updateSlideTitle(slideIdx, e.target.value)}
                    className="w-full mb-3 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <div className="space-y-2">
                    {slide.content.map((bullet, bulletIdx) => (
                      <div key={bulletIdx} className="flex space-x-2">
                        <input
                          type="text"
                          placeholder="• Bullet point"
                          value={bullet}
                          onChange={(e) =>
                            updateBulletPoint(slideIdx, bulletIdx, e.target.value)
                          }
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        {slide.content.length > 1 && (
                          <button
                            onClick={() => removeBulletPoint(slideIdx, bulletIdx)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                  <button
                    onClick={() => addBulletPoint(slideIdx)}
                    className="mt-2 text-sm text-blue-600 hover:text-blue-700"
                  >
                    + Add Bullet Point
                  </button>
                </div>
              ))}
            </div>

            <button
              onClick={addSlide}
              className="mt-4 flex items-center text-blue-600 hover:text-blue-700"
            >
              <Plus className="w-4 h-4 mr-1" />
              Add Slide
            </button>
          </div>
        )}

        {/* Format & Generate */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Export</h2>
          <div className="flex items-center space-x-4 mb-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="pptx"
                checked={format === "pptx"}
                onChange={(e) => setFormat(e.target.value as "pptx" | "pdf")}
                className="mr-2"
              />
              PPTX
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="pdf"
                checked={format === "pdf"}
                onChange={(e) => setFormat(e.target.value as "pptx" | "pdf")}
                className="mr-2"
              />
              PDF
            </label>
          </div>
          <button
            onClick={handleGenerateSlides}
            disabled={isGeneratingSlides}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center space-x-2"
          >
            {isGeneratingSlides ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Generating Presentation...</span>
              </>
            ) : (
              <>
                <Presentation className="w-5 h-5" />
                <span>Generate Presentation</span>
              </>
            )}
          </button>
        </div>

        {/* Download Link */}
        {downloadUrl && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-green-900 mb-1">
                  Presentation Ready!
                </h3>
                <p className="text-sm text-green-700">
                  {generatedSlideCount} slides generated successfully
                </p>
              </div>
              <a
                href={downloadUrl}
                download
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center space-x-2"
              >
                <Download className="w-5 h-5" />
                <span>Download</span>
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

