"use client";

import { useState } from "react";

interface CvFormProps {
  onSubmit: (data: any) => void;
  locale?: "ar" | "en";
}

export function CvForm({ onSubmit, locale = "ar" }: CvFormProps) {
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    phone: "",
    title: "",
    summary: "",
    skills: [] as string[],
    education: [] as any[],
    experience: [] as any[],
    ats_friendly: true,
    export_format: "pdf" as "pdf" | "docx",
  });

  const isArabic = locale === "ar";

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ ...formData, locale });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold">
        {isArabic ? "صانع السيرة الذاتية" : "CV Maker"}
      </h2>

      {/* Personal Info */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">
          {isArabic ? "المعلومات الشخصية" : "Personal Information"}
        </h3>

        <div>
          <label className="block text-sm font-medium mb-1">
            {isArabic ? "الاسم الكامل" : "Full Name"}
          </label>
          <input
            type="text"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            required
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              {isArabic ? "البريد الإلكتروني" : "Email"}
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
              className="w-full px-3 py-2 border rounded"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">
              {isArabic ? "الهاتف" : "Phone"}
            </label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className="w-full px-3 py-2 border rounded"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            {isArabic ? "المسمى الوظيفي" : "Job Title"}
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            required
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            {isArabic ? "الملخص المهني" : "Professional Summary"}
          </label>
          <textarea
            value={formData.summary}
            onChange={(e) => setFormData({ ...formData, summary: e.target.value })}
            required
            rows={4}
            className="w-full px-3 py-2 border rounded"
          />
        </div>
      </div>

      {/* Options */}
      <div className="space-y-4">
        <div className="flex items-center">
          <input
            type="checkbox"
            id="ats"
            checked={formData.ats_friendly}
            onChange={(e) => setFormData({ ...formData, ats_friendly: e.target.checked })}
            className="mr-2"
          />
          <label htmlFor="ats" className="text-sm">
            {isArabic
              ? "تحسين لأنظمة ATS"
              : "Optimize for ATS Systems"}
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            {isArabic ? "صيغة التصدير" : "Export Format"}
          </label>
          <select
            value={formData.export_format}
            onChange={(e) =>
              setFormData({ ...formData, export_format: e.target.value as "pdf" | "docx" })
            }
            className="w-full px-3 py-2 border rounded"
          >
            <option value="pdf">PDF</option>
            <option value="docx">DOCX</option>
          </select>
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit"
        className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
      >
        {isArabic ? "إنشاء السيرة الذاتية" : "Generate CV"}
      </button>
    </form>
  );
}

