"use client";

import { FormEvent, useRef } from "react";

interface Props {
  onSubmit: (query: string) => void;
  loading: boolean;
}

const SUGGESTED = [
  "Why does the curve taper at high SOC?",
  "What's the difference between NMC and LFP?",
  "Why do 800V cars charge faster?",
];

export default function ChatInput({ onSubmit, loading }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);

  function submit(query: string) {
    onSubmit(query);
    if (inputRef.current) inputRef.current.value = "";
  }

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const query = inputRef.current?.value.trim();
    if (query) submit(query);
  }

  return (
    <div className="space-y-2">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          ref={inputRef}
          type="text"
          placeholder="Ask about charging behavior, chemistry, or BMS..."
          className="flex-1 rounded-lg border border-gray-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-gray-900 px-6 py-3 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50 transition-colors"
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </form>
      <div className="flex flex-wrap gap-2">
        {SUGGESTED.map((q) => (
          <button
            key={q}
            type="button"
            onClick={() => submit(q)}
            disabled={loading}
            className="rounded-full border border-gray-200 bg-white px-3 py-1 text-xs text-gray-600 hover:border-gray-300 hover:text-gray-900 disabled:opacity-50 transition-colors"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
