"use client";

import { ChatInterface } from "@/components/ChatInterface";
import { Sidebar } from "@/components/Sidebar";

export default function ChatPage() {
  return (
    <div className="flex h-screen">
      <Sidebar locale="ar" />
      <div className="flex-1 flex flex-col">
        <ChatInterface />
      </div>
    </div>
  );
}
