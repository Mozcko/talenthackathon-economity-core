interface Investment {
  id: number;
  entidad: string;
  tipo: string;
  monto: number;
  tasa: number;
}

interface InvestmentCardProps {
  investment: Investment;
}

export default function InvestmentCard({ investment }: InvestmentCardProps) {
  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(value);

  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between p-5 rounded-2xl border border-gray-100 hover:shadow-md transition-all duration-300 bg-gray-50/50 group cursor-default">
      <div className="flex items-center space-x-4 mb-4 sm:mb-0">
        <div className="w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold text-lg group-hover:scale-110 transition-transform">
          {investment.entidad.charAt(0)}
        </div>
        <div>
          <h4 className="text-gray-800 font-bold text-lg group-hover:text-indigo-600 transition-colors">
            {investment.entidad}
          </h4>
          <p className="text-sm text-gray-500 font-medium">{investment.tipo}</p>
        </div>
      </div>
      
      <div className="flex flex-row sm:flex-col justify-between sm:items-end items-center">
        <span className="text-gray-800 font-extrabold text-xl">
          {formatCurrency(investment.monto)}
        </span>
        <span className="text-emerald-500 font-bold text-sm flex items-center gap-1 mt-1 bg-emerald-50 px-2 py-0.5 rounded-md">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
          {(investment.tasa * 100).toFixed(2)}% anual
        </span>
      </div>
    </div>
  );
}