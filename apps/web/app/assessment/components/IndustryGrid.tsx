"use client";

interface Industry {
  value: string;
  label: string;
}

interface IndustryGridProps {
  industries: Industry[];
  value: string;
  onChange: (value: string) => void;
}

export default function IndustryGrid({ industries, value, onChange }: IndustryGridProps) {
  return (
    <div className="grid grid-cols-2 gap-3">
      {industries.map((industry) => (
        <button
          key={industry.value}
          type="button"
          onClick={() => onChange(industry.value)}
          className={`px-4 py-3 rounded-xl border-2 transition-all text-sm font-medium ${
            value === industry.value
              ? "bg-gradient-to-br from-purple-600 to-cyan-600 border-purple-500 text-white shadow-lg"
              : "bg-slate-700 border-slate-600 text-gray-300 active:bg-slate-600"
          }`}
        >
          {industry.label}
        </button>
      ))}
    </div>
  );
}

