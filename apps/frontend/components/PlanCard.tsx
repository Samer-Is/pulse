"use client";

import { PayButton } from "./PayButton";

interface PlanCardProps {
  planId: string;
  name: string;
  nameAr: string;
  price: number;
  tokenLimit: number;
  imageLimit: number;
  videoLimit: number;
  features: string[];
  featuresAr: string[];
  popular?: boolean;
  locale?: "ar" | "en";
}

export function PlanCard({
  planId,
  name,
  nameAr,
  price,
  tokenLimit,
  imageLimit,
  videoLimit,
  features,
  featuresAr,
  popular = false,
  locale = "ar",
}: PlanCardProps) {
  const isArabic = locale === "ar";
  const displayName = isArabic ? nameAr : name;
  const displayFeatures = isArabic ? featuresAr : features;

  return (
    <div
      className={`relative bg-white rounded-2xl shadow-lg p-6 ${
        popular ? "ring-4 ring-blue-500 scale-105" : ""
      }`}
    >
      {popular && (
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
          {isArabic ? "الأكثر شعبية" : "Most Popular"}
        </div>
      )}

      <h3 className="text-2xl font-bold text-gray-900 mb-2">{displayName}</h3>

      <div className="text-4xl font-bold text-blue-600 mb-4">
        {price}{" "}
        <span className="text-lg text-gray-600">
          {isArabic ? "د.أ/شهر" : "JD/mo"}
        </span>
      </div>

      <div className="space-y-2 mb-6">
        <div className="text-sm text-gray-600">
          ✅ {tokenLimit.toLocaleString()} {isArabic ? "رمز" : "tokens"}
        </div>
        <div className="text-sm text-gray-600">
          ✅ {imageLimit} {isArabic ? "صورة" : "images"}
        </div>
        <div className="text-sm text-gray-600">
          ✅ {videoLimit} {isArabic ? "فيديو" : "videos"}
        </div>
      </div>

      <ul className="space-y-2 mb-6">
        {displayFeatures.map((feature, index) => (
          <li key={index} className="text-sm text-gray-700">
            ✅ {feature}
          </li>
        ))}
      </ul>

      <PayButton planId={planId} planName={displayName} locale={locale} />
    </div>
  );
}

