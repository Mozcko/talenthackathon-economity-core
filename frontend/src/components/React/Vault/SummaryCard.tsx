interface SummaryCardProps {
  title: string;
  value: string;
  subtitle?: string;
  trend?: string;
}

export default function SummaryCard({ title, value, subtitle, trend }: SummaryCardProps) {
  return (
    <div className="bg-surface-container-lowest p-6 rounded-2xl shadow-sm border border-outline-variant/20 flex flex-col justify-between hover:shadow-md transition-shadow">
      <div>
        <p className="text-xs font-bold text-on-surface/50 uppercase tracking-widest">{title}</p>
        <h3 className="text-4xl font-black text-on-surface mt-2">{value}</h3>
      </div>
      <div className="mt-6 flex items-center justify-between">
        {subtitle && <p className="text-sm text-on-surface/40 font-medium">{subtitle}</p>}
        {trend && (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-[10px] font-bold bg-secondary/10 text-secondary uppercase tracking-tight">
            {trend}
          </span>
        )}
      </div>
    </div>
  );
}