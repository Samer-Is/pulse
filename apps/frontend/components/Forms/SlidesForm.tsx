"use client";

import { useState } from "react";

interface SlidesFormProps {
  onSubmit: (data: any) => void;
  locale?: "ar" | "en";
}

export function SlidesForm({ onSubmit, locale = "ar" }: SlidesFormProps) {
  const [formData, setFormData] = useState({
    presentation_title: "",
    author: "",
    topic: "",
    audience: "",
    num_slides: 10,
    theme: "professional" as "professional" | "modern" | "minimal",
    export_format: "pptx" as "pptx" | "pdf",
  });

  const isArabic = locale === "ar";

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ ...formData, locale });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold">
        {isArabic ? "صانع العروض التقديمية" : "Slides Maker"}
      </h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            {isArabic ? "عنوان العرض" : "Presentation Title"}
          </label>
          <input
            type="text"
            value={formData.presentation_title}
            onChange={(e) =>
              setFormData({ ...formData, presentation_title: e.target.value })
            }
            required
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            {isArabic ? "المؤلف" : "Author"}
          </label>
          <input
            type="text"
            value={formData.author}
            onChange={(e) => setFormData({ ...formData, author: e.target.value })}
            required
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            {isArabic ? "الموضوع" : "Topic"}
          </label>
          <textarea
            value={formData.topic}
            onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
            required
            rows={3}
            placeholder={isArabic ? "صف موضوع عرضك التقديمي" : "Describe your presentation topic"}
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            {isArabic ? "الجمهور المستهدف" : "Target Audience"}
          </label>
          <input
            type="text"
            value={formData.audience}
            onChange={(e) => setFormData({ ...formData, audience: e.target.value })}
            placeholder={isArabic ? "مثال: مدراء الشركات" : "e.g., Business executives"}
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            {isArabic ? "عدد الشرائح" : "Number of Slides"}
          </label>
          <input
            type="number"
            value={formData.num_slides}
            onChange={(e) =>
              setFormData({ ...formData, num_slides: parseInt(e.target.value) })
            }
            min={5}
            max={50}
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            {isArabic ? "القالب" : "Theme"}
          </label>
          <select
            value={formData.theme}
            onChange={(e) =>
              setFormData({
                ...formData,
                theme: e.target.value as "professional" | "modern" | "minimal",
              })
            }
            className="w-full px-3 py-2 border rounded"
          >
            <option value="professional">
              {isArabic ? "احترافي" : "Professional"}
            </option>
            <option value="modern">{isArabic ? "عصري" : "Modern"}</option>
            <option value="minimal">{isArabic ? "بسيط" : "Minimal"}</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            {isArabic ? "صيغة التصدير" : "Export Format"}
          </label>
          <select
            value={formData.export_format}
            onChange={(e) =>
              setFormData({ ...formData, export_format: e.target.value as "pptx" | "pdf" })
            }
            className="w-full px-3 py-2 border rounded"
          >
            <option value="pptx">PowerPoint (PPTX)</option>
            <option value="pdf">PDF</option>
          </select>
        </div>
      </div>

      <button
        type="submit"
        className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
      >
        {isArabic ? "إنشاء العرض التقديمي" : "Generate Slides"}
      </button>
    </form>
  );
}

