interface SummaryCardProps {
  title: string;
  value: string;
  subtitle?: string;
  trend?: string;
}

export default function SummaryCard({ title, value, subtitle, trend }: SummaryCardProps) {
  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between hover:shadow-md transition-shadow">
      <div>
        <p className="text-sm font-medium text-gray-500 uppercase tracking-wider">{title}</p>
        <h3 className="text-4xl font-extrabold text-gray-800 mt-2">{value}</h3>
      </div>
      <div className="mt-6 flex items-center justify-between">
        {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
        {trend && (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700">
            {trend}
          </span>
        )}
      </div>
    </div>
  );
}