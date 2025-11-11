"use client";

import { useState } from "react";

interface VideoEditorProps {
  videoUrl: string;
  onSave: (editedUrl: string) => void;
  locale?: "ar" | "en";
}

export function VideoEditor({ videoUrl, onSave, locale = "ar" }: VideoEditorProps) {
  const [trimStart, setTrimStart] = useState(0);
  const [trimEnd, setTrimEnd] = useState(10);
  const [captions, setCaptions] = useState("");
  const isArabic = locale === "ar";

  const handleSave = () => {
    // In production: Submit to worker for FFmpeg processing
    // For now, return original URL
    onSave(videoUrl);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-xl font-bold mb-4">
        {isArabic ? "محرر الفيديو" : "Video Editor"}
      </h3>

      {/* Video Preview */}
      <div className="mb-4">
        <video
          src={videoUrl}
          controls
          className="w-full max-h-96 mx-auto border rounded"
        />
      </div>

      {/* Editing Tools */}
      <div className="space-y-4">
        {/* Trim Tool */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {isArabic ? "قص الفيديو (ثواني)" : "Trim Video (seconds)"}
          </label>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-xs text-gray-500">
                {isArabic ? "البداية" : "Start"}
              </label>
              <input
                type="number"
                value={trimStart}
                onChange={(e) => setTrimStart(parseInt(e.target.value))}
                min={0}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500">
                {isArabic ? "النهاية" : "End"}
              </label>
              <input
                type="number"
                value={trimEnd}
                onChange={(e) => setTrimEnd(parseInt(e.target.value))}
                min={trimStart}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
          </div>
        </div>

        {/* Captions */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {isArabic ? "إضافة ترجمات" : "Add Captions"}
          </label>
          <textarea
            value={captions}
            onChange={(e) => setCaptions(e.target.value)}
            placeholder={isArabic ? "أدخل النص" : "Enter text"}
            rows={3}
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
        >
          {isArabic ? "حفظ التعديلات" : "Save Changes"}
        </button>

        <p className="text-xs text-gray-500 text-center">
          {isArabic
            ? "⏳ معالجة الفيديو قد تستغرق عدة دقائق"
            : "⏳ Video processing may take several minutes"}
        </p>
      </div>
    </div>
  );
}

