"use client";

interface StepperProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
}

export default function Stepper({ label, value, onChange, min = 0, max = 10 }: StepperProps) {
  return (
    <div className="flex items-center justify-between p-4 bg-slate-700 rounded-xl">
      <span className="text-gray-300 font-medium">{label}</span>
      <div className="flex items-center gap-4">
        <button
          type="button"
          onClick={() => onChange(Math.max(min, value - 1))}
          disabled={value <= min}
          className="w-10 h-10 rounded-lg bg-slate-600 text-white font-bold text-lg disabled:opacity-50 disabled:cursor-not-allowed active:bg-slate-500"
        >
          -
        </button>
        <span className="text-white text-xl font-semibold w-8 text-center">{value}</span>
        <button
          type="button"
          onClick={() => onChange(Math.min(max, value + 1))}
          disabled={value >= max}
          className="w-10 h-10 rounded-lg bg-slate-600 text-white font-bold text-lg disabled:opacity-50 disabled:cursor-not-allowed active:bg-slate-500"
        >
          +
        </button>
      </div>
    </div>
  );
}

