"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { TokenMeter } from "./TokenMeter";

const navigation = [
  { name: "الدردشة", nameEn: "Chat", href: "/app/chat", icon: "💬" },
  { name: "صانع السيرة", nameEn: "CV Maker", href: "/app/cv", icon: "📄" },
  { name: "صانع العروض", nameEn: "Slides", href: "/app/slides", icon: "📊" },
  { name: "محرر الصور", nameEn: "Images", href: "/app/images", icon: "🖼️" },
  { name: "محرر الفيديو", nameEn: "Video", href: "/app/video", icon: "🎬" },
];

interface SidebarProps {
  locale?: "ar" | "en";
}

export function Sidebar({ locale = "ar" }: SidebarProps) {
  const pathname = usePathname();
  const isArabic = locale === "ar";

  return (
    <div className="flex flex-col h-full w-64 bg-gray-900 text-white">
      {/* Logo */}
      <div className="p-4 border-b border-gray-800">
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-2xl font-bold">Pulse AI</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition ${
                isActive
                  ? "bg-blue-600 text-white"
                  : "text-gray-300 hover:bg-gray-800 hover:text-white"
              }`}
            >
              <span className="text-2xl">{item.icon}</span>
              <span className="font-medium">
                {isArabic ? item.name : item.nameEn}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* Usage Meter */}
      <div className="p-4 border-t border-gray-800">
        <TokenMeter />
      </div>

      {/* Account */}
      <div className="p-4 border-t border-gray-800">
        <Link
          href="/app/account"
          className="flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-800 hover:text-white transition"
        >
          <span className="text-2xl">⚙️</span>
          <span className="font-medium">{isArabic ? "الحساب" : "Account"}</span>
        </Link>
      </div>
    </div>
  );
}

