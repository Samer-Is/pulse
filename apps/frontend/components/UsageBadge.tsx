"use client";

interface UsageBadgeProps {
  used: number;
  limit: number;
  label: string;
  locale?: "ar" | "en";
}

export function UsageBadge({ used, limit, label, locale = "ar" }: UsageBadgeProps) {
  const percentage = (used / limit) * 100;
  const isArabic = locale === "ar";

  // Determine color based on usage
  let bgColor = "bg-green-100";
  let textColor = "text-green-800";
  let barColor = "bg-green-500";

  if (percentage >= 100) {
    bgColor = "bg-red-100";
    textColor = "text-red-800";
    barColor = "bg-red-500";
  } else if (percentage >= 80) {
    bgColor = "bg-yellow-100";
    textColor = "text-yellow-800";
    barColor = "bg-yellow-500";
  }

  return (
    <div className={`${bgColor} rounded-lg p-3`}>
      <div className="flex justify-between items-center mb-2">
        <span className={`text-sm font-medium ${textColor}`}>{label}</span>
        <span className={`text-sm font-bold ${textColor}`}>
          {used.toLocaleString()} / {limit.toLocaleString()}
        </span>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`${barColor} h-2 rounded-full transition-all duration-300`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        ></div>
      </div>

      {percentage >= 80 && percentage < 100 && (
        <p className="text-xs text-yellow-700 mt-2">
          {isArabic
            ? "⚠️ اقتربت من الحد الأقصى"
            : "⚠️ Approaching limit"}
        </p>
      )}

      {percentage >= 100 && (
        <p className="text-xs text-red-700 mt-2">
          {isArabic ? "❌ تم تجاوز الحد" : "❌ Limit reached"}
        </p>
      )}
    </div>
  );
}

