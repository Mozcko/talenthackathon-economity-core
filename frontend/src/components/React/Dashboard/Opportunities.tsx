interface Opportunity {
  name: string;
  yieldRate: number;
  period: string;
}

const mockOpportunities: Opportunity[] = [
  { name: 'Finsus', yieldRate: 10.09, period: 'GAT nominal' },
  { name: 'Nu', yieldRate: 14.50, period: 'anualizado' },
  { name: 'Cetes', yieldRate: 11.25, period: 'mensual' },
];

export default function Opportunities() {
  return (
    <div className="w-full space-y-4">
      <h2 className="text-xl font-display font-bold text-primary">Oportunidades para tu dinero</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {mockOpportunities.map((opp, index) => (
          <div key={index} className="bg-surface-container-lowest p-6 rounded-2xl border border-outline-variant/30 shadow-ambient hover:scale-[1.02] transition-transform cursor-pointer">
            <h3 className="text-lg font-bold text-primary">{opp.name}</h3>
            <div className="mt-2 flex items-baseline gap-1">
              <span className="text-3xl font-bold text-secondary">{opp.yieldRate.toFixed(2)}%</span>
              <span className="text-sm text-on-surface/60 font-medium">{opp.period}</span>
            </div>
          </div>
        ))}
        
        {/* Explore More Card */}
        <div className="bg-surface-container-low p-6 rounded-2xl border-2 border-dashed border-outline-variant/50 flex flex-col items-center justify-center text-center hover:bg-surface-container-high transition-colors cursor-pointer min-h-[120px]">
          <span className="text-primary font-bold text-lg">Explorar más</span>
          <svg className="w-6 h-6 mt-2 text-on-surface/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </div>
      </div>
    </div>
  );
}