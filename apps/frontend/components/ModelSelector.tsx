"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { chat } from "@/lib/api";

interface Model {
  id: string;
  name: string;
  provider: string;
  context_window: number;
  available?: boolean;
}

interface ModelSelectorProps {
  value: string;
  onChange: (modelId: string) => void;
  disabled?: boolean;
}

export function ModelSelector({ value, onChange, disabled }: ModelSelectorProps) {
  const { data: models, isLoading } = useQuery({
    queryKey: ["chat-models"],
    queryFn: () => chat.listModels(),
  });

  const selectedModel = models?.models?.find((m: Model) => m.id === value);

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg">
        <div className="animate-pulse w-32 h-4 bg-gray-300 rounded"></div>
      </div>
    );
  }

  return (
    <div className="relative">
      <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-1">
        نموذج الذكاء الاصطناعي
      </label>
      <select
        id="model"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {models?.models
          ?.filter((m: Model) => m.available !== false)
          .map((model: Model) => (
            <option key={model.id} value={model.id}>
              {model.name} ({model.provider})
            </option>
          ))}
      </select>
      
      {selectedModel && (
        <p className="mt-1 text-xs text-gray-500">
          Context: {selectedModel.context_window.toLocaleString()} tokens
        </p>
      )}
    </div>
  );
}

