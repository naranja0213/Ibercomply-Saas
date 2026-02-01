"use client";

import { useState } from "react";

interface Signal {
  key: string;
  label: string;
  description: string;
}

interface SignalsPanelProps {
  signals: Signal[];
  values: Record<string, boolean>;
  onChange: (key: string, value: boolean) => void;
}

export default function SignalsPanel({ signals, values, onChange }: SignalsPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (signals.length === 0) return null;

  return (
    <div className="bg-slate-800 rounded-xl overflow-hidden">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 flex items-center justify-between text-left"
      >
        <span className="text-gray-300 font-medium">行业细节（可选，越准越好）</span>
        <span className={`text-purple-400 transition-transform ${isOpen ? "rotate-180" : ""}`}>
          ▼
        </span>
      </button>
      {isOpen && (
        <div className="px-4 pb-4 space-y-3 border-t border-slate-700 pt-3">
          {signals.map((signal) => (
            <label
              key={signal.key}
              className="flex items-start space-x-3 cursor-pointer p-3 rounded-lg hover:bg-slate-700 transition-colors"
            >
              <input
                type="checkbox"
                checked={values[signal.key] || false}
                onChange={(e) => onChange(signal.key, e.target.checked)}
                className="mt-1 w-5 h-5 rounded border-slate-600 bg-slate-700 text-purple-600 focus:ring-purple-500"
              />
              <div className="flex-1">
                <div className="text-white font-medium text-sm">{signal.label}</div>
                <div className="text-gray-400 text-xs mt-1">{signal.description}</div>
              </div>
            </label>
          ))}
        </div>
      )}
    </div>
  );
}

