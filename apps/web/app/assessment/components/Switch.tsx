"use client";

interface SwitchProps {
  label: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
}

export default function Switch({ label, checked, onCheckedChange }: SwitchProps) {
  return (
    <div className="flex items-center justify-between p-4 bg-slate-700 rounded-xl">
      <span className="text-gray-300 font-medium">{label}</span>
      <button
        type="button"
        onClick={() => onCheckedChange(!checked)}
        className={`relative w-14 h-8 rounded-full transition-colors ${
          checked ? "bg-purple-600" : "bg-slate-600"
        }`}
      >
        <span
          className={`absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform ${
            checked ? "translate-x-6" : "translate-x-0"
          }`}
        />
      </button>
    </div>
  );
}

