import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "../styles/globals.css";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Pulse AI Studio - Arabic-First AI Workspace",
  description: "All-in-one AI platform for chat, images, videos, CVs, and presentations",
  keywords: ["AI", "Arabic", "Jordan", "Chat", "Images", "Video", "CV", "Slides"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ar" dir="rtl">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
