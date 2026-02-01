"use client";

interface RevenueSegmentProps {
  options: number[];
  value: number | null;
  onChange: (value: number) => void;
}

export default function RevenueSegment({ options, value, onChange }: RevenueSegmentProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
      {options.map((income) => (
        <button
          key={income}
          type="button"
          onClick={() => onChange(income)}
          className={`px-4 py-2 rounded-lg whitespace-nowrap font-medium transition-all ${
            value === income
              ? "bg-purple-600 text-white shadow-md"
              : "bg-slate-700 text-gray-300 active:bg-slate-600"
          }`}
        >
          €{income}
        </button>
      ))}
    </div>
  );
}

