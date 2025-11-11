"use client";

import { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { CvForm } from "@/components/Forms/CvForm";

export default function CVPage() {
  const [generatedCV, setGeneratedCV] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (data: any) => {
    setLoading(true);
    try {
      // TODO: Call backend API
      // const result = await cv.generate(data);
      // setGeneratedCV(result.download_url);
      
      alert("CV generation coming soon!");
    } catch (error: any) {
      alert(error.message || "CV generation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen">
      <Sidebar locale="ar" />
      <div className="flex-1 overflow-y-auto p-8 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <CvForm onSubmit={handleSubmit} locale="ar" />

          {loading && (
            <div className="mt-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">جارٍ إنشاء السيرة الذاتية...</p>
            </div>
          )}

          {generatedCV && (
            <div className="mt-8 bg-white rounded-lg shadow p-6">
              <h3 className="text-xl font-bold mb-4">سيرتك الذاتية جاهزة! ✅</h3>
              <a
                href={generatedCV}
                download
                className="inline-block px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700"
              >
                تحميل السيرة الذاتية
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

