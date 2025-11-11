"use client";

import { useState } from "react";

interface ImageEditorProps {
  imageUrl: string;
  onSave: (editedUrl: string) => void;
  locale?: "ar" | "en";
}

export function ImageEditor({ imageUrl, onSave, locale = "ar" }: ImageEditorProps) {
  const [crop, setCrop] = useState({ x: 0, y: 0, width: 100, height: 100 });
  const [text, setText] = useState("");
  const isArabic = locale === "ar";

  const handleSave = () => {
    // In production: Apply edits using canvas API or image processing library
    // For now, return original URL
    onSave(imageUrl);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-xl font-bold mb-4">
        {isArabic ? "محرر الصور" : "Image Editor"}
      </h3>

      {/* Image Preview */}
      <div className="mb-4">
        <img
          src={imageUrl}
          alt="Editing"
          className="max-w-full max-h-96 mx-auto border rounded"
        />
      </div>

      {/* Basic Tools */}
      <div className="space-y-4">
        {/* Crop Tool */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {isArabic ? "اقتصاص" : "Crop"}
          </label>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="number"
              placeholder="Width"
              value={crop.width}
              onChange={(e) => setCrop({ ...crop, width: parseInt(e.target.value) })}
              className="px-3 py-2 border rounded"
            />
            <input
              type="number"
              placeholder="Height"
              value={crop.height}
              onChange={(e) => setCrop({ ...crop, height: parseInt(e.target.value) })}
              className="px-3 py-2 border rounded"
            />
          </div>
        </div>

        {/* Text Overlay */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {isArabic ? "إضافة نص" : "Add Text"}
          </label>
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={isArabic ? "أدخل النص" : "Enter text"}
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
      </div>
    </div>
  );
}

