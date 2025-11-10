"use client";

import { useQuery } from "@tanstack/react-query";
import { usage } from "@/lib/api";

interface UsageData {
  period: {
    start: string;
    end: string;
  };
  plan: {
    name: string;
    limits: {
      tokens: number;
      images: number;
      videos: number;
    };
  };
  usage: {
    tokens: {
      used: number;
      remaining: number;
      percentage: number;
    };
    images: {
      used: number;
      remaining: number;
      percentage: number;
    };
    videos: {
      used: number;
      remaining: number;
      percentage: number;
    };
  };
  warnings: {
    tokens: boolean;
    images: boolean;
    videos: boolean;
  };
}

export function TokenMeter() {
  const { data, isLoading, error } = useQuery<UsageData>({
    queryKey: ["usage"],
    queryFn: () => usage.getCurrent(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  if (isLoading) {
    return (
      <div className="animate-pulse p-4 bg-gray-100 rounded-lg">
        <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
        <div className="h-2 bg-gray-300 rounded w-full"></div>
      </div>
    );
  }

  if (error || !data) {
    return null;
  }

  const getColorClass = (percentage: number, warning: boolean) => {
    if (percentage >= 100) return "bg-red-500";
    if (warning || percentage >= 80) return "bg-yellow-500";
    return "bg-blue-500";
  };

  const getTextColorClass = (percentage: number, warning: boolean) => {
    if (percentage >= 100) return "text-red-600";
    if (warning || percentage >= 80) return "text-yellow-600";
    return "text-gray-600";
  };

  return (
    <div className="space-y-4">
      {/* Plan Info */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">
          خطة {data.plan.name}
        </h3>
        <span className="text-xs text-gray-500">
          {new Date(data.period.end).toLocaleDateString("ar")}
        </span>
      </div>

      {/* Tokens */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <span className={`text-sm font-medium ${getTextColorClass(data.usage.tokens.percentage, data.warnings.tokens)}`}>
            الكلمات
          </span>
          <span className="text-sm text-gray-600">
            {data.usage.tokens.used.toLocaleString()} / {data.usage.tokens.used + data.usage.tokens.remaining.toLocaleString()}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${getColorClass(data.usage.tokens.percentage, data.warnings.tokens)}`}
            style={{ width: `${Math.min(data.usage.tokens.percentage, 100)}%` }}
          ></div>
        </div>
      </div>

      {/* Images */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <span className={`text-sm font-medium ${getTextColorClass(data.usage.images.percentage, data.warnings.images)}`}>
            الصور
          </span>
          <span className="text-sm text-gray-600">
            {data.usage.images.used} / {data.usage.images.used + data.usage.images.remaining}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${getColorClass(data.usage.images.percentage, data.warnings.images)}`}
            style={{ width: `${Math.min(data.usage.images.percentage, 100)}%` }}
          ></div>
        </div>
      </div>

      {/* Videos */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <span className={`text-sm font-medium ${getTextColorClass(data.usage.videos.percentage, data.warnings.videos)}`}>
            الفيديوهات
          </span>
          <span className="text-sm text-gray-600">
            {data.usage.videos.used} / {data.usage.videos.used + data.usage.videos.remaining}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${getColorClass(data.usage.videos.percentage, data.warnings.videos)}`}
            style={{ width: `${Math.min(data.usage.videos.percentage, 100)}%` }}
          ></div>
        </div>
      </div>

      {/* Warnings */}
      {(data.warnings.tokens || data.warnings.images || data.warnings.videos) && (
        <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-xs text-yellow-800">
            ⚠️ أوشكت على استنفاد حصتك الشهرية
          </p>
        </div>
      )}

      {/* Quota Exceeded */}
      {(data.usage.tokens.percentage >= 100 || data.usage.images.percentage >= 100 || data.usage.videos.percentage >= 100) && (
        <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-xs text-red-800">
            ❌ تم استنفاد حصتك الشهرية
          </p>
          <a href="/app/account/upgrade" className="text-xs text-red-600 underline">
            ترقية الخطة
          </a>
        </div>
      )}
    </div>
  );
}

