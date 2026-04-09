interface Expense {
  id: number;
  comercio: string;
  categoria: string;
  monto: number;
  fecha: string;
}

interface ExpenseCardProps {
  expense: Expense;
}

export default function ExpenseCard({ expense }: ExpenseCardProps) {
  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(value);

  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between p-5 rounded-2xl border border-outline-variant/10 hover:shadow-md transition-all duration-300 bg-surface-container-lowest/50 group cursor-default">
      <div className="flex items-center space-x-4 mb-4 sm:mb-0">
        <div className="w-12 h-12 rounded-xl bg-rose-100 flex items-center justify-center text-rose-600 font-bold text-lg group-hover:scale-110 transition-transform">
          {expense.comercio.charAt(0)}
        </div>
        <div>
          <h4 className="text-on-surface font-bold text-lg group-hover:text-rose-600 transition-colors">
            {expense.comercio}
          </h4>
          <p className="text-sm text-on-surface/50 font-medium">{expense.categoria}</p>
        </div>
      </div>
      
      <div className="flex flex-row sm:flex-col justify-between sm:items-end items-center">
        <span className="text-on-surface font-extrabold text-xl">
          {formatCurrency(expense.monto)}
        </span>
        <span className="text-on-surface/40 font-bold text-xs mt-1">
          {expense.fecha}
        </span>
      </div>
    </div>
  );
}