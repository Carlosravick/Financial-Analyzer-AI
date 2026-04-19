import React from "react";

interface DashboardCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
}

export function DashboardCard({ title, value, icon }: DashboardCardProps) {
  return (
    <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl flex flex-col justify-between h-full">
      <div className="flex justify-between items-start mb-4">
        <span className="text-slate-400 font-medium text-sm">{title}</span>
        <div className="p-2 bg-slate-900 rounded-lg">{icon}</div>
      </div>
      <div className="text-3xl font-bold text-slate-100 mt-auto">{value}</div>
    </div>
  );
}
