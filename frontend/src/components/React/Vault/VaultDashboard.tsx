import { useState, useEffect } from 'react';
import SummaryCard from './SummaryCard';
import AssetDistributionChart from './AssetDistributionChart';
import ExpenseCard from './InvestmentCard';

// Mock Data de Gastos
const mockDashboard = { gasto_total: 15420.30, presupuesto_restante: 4579.70 };
const mockExpenses = [
  { id: 1, comercio: "Chedraui", categoria: "Súper", monto: 3200.50, fecha: "Hoy" },
  { id: 2, comercio: "Gasolinera Pemex", categoria: "Transporte", monto: 950.00, fecha: "Ayer" },
  { id: 3, comercio: "Netflix", categoria: "Suscripciones", monto: 219.00, fecha: "15 Mar" },
  { id: 4, comercio: "Restaurante El Faro", categoria: "Comida", monto: 1250.00, fecha: "14 Mar" },
  { id: 5, comercio: "CFE", categoria: "Servicios", monto: 850.00, fecha: "12 Mar" },
  { id: 6, comercio: "Amazon", categoria: "Compras", monto: 2450.80, fecha: "10 Mar" }
];

export default function ExpensesDashboard() {
  const [loading, setLoading] = useState(true);
  const [visible, setVisible] = useState(false);
  const [dashboardData, setDashboardData] = useState<{ gasto_total: number; presupuesto_restante: number } | null>(null);
  const [expenseData, setExpenseData] = useState<any[]>([]);

  // Simulación de carga de 1 segundo
  useEffect(() => {
    const timer = setTimeout(() => {
      setDashboardData(mockDashboard);
      setExpenseData(mockExpenses);
      setLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  // Trigger fade-in after loading finishes and content is rendered
  useEffect(() => {
    if (!loading) {
      const raf = requestAnimationFrame(() => setVisible(true));
      return () => cancelAnimationFrame(raf);
    }
  }, [loading]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-rose-600"></div>
      </div>
    );
  }

  if (!dashboardData) return null;

  return (
    <div
    className="m-5 ml-5 max-w-7xl mx-auto space-y-8"
    style={{
      opacity: visible ? 1 : 0,
      transform: visible ? 'translateY(0)' : 'translateY(16px)',
      transition: 'opacity 0.5s ease, transform 0.5s ease',
    }}
  >
      <header>
        <h1 className="text-3xl font-bold text-on-surface tracking-tight">Mis Gastos</h1>
        <p className="text-on-surface/50 mt-1">Control y Categorización Mensual</p>
      </header>

      {/* Top: Tarjetas de resumen */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <SummaryCard
          title="Gasto Total Mensual"
          value={new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(dashboardData.gasto_total)}
          subtitle="Total acumulado en el periodo"
          trend="Dentro del límite"
        />
        <SummaryCard
          title="Presupuesto Restante"
          value={new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(dashboardData.presupuesto_restante)}
          subtitle="Disponible para el resto del mes"
          trend="Sugerencia: Ahorrar 10%"
        />
      </section>

      {/* Middle & Bottom: Gráfica y Lista de Gastos */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <section className="lg:col-span-1 bg-surface-container-lowest p-6 rounded-2xl shadow-sm border border-outline-variant/20 flex flex-col">
          <h2 className="text-xl font-bold text-on-surface mb-6">Distribución por Categoría</h2>
          <div className="flex-1 flex items-center justify-center min-h-[300px]">
            <AssetDistributionChart data={expenseData} />
          </div>
        </section>

        <section className="lg:col-span-2 bg-surface-container-lowest p-6 rounded-2xl shadow-sm border border-outline-variant/20 flex flex-col space-y-4">
          <h2 className="text-xl font-bold text-on-surface mb-2">Historial de Gastos</h2>
          {expenseData.map((exp, index) => (
            <div
              key={exp.id}
              style={{
                opacity: visible ? 1 : 0,
                transform: visible ? 'translateY(0)' : 'translateY(16px)',
                transition: `opacity 0.5s ease ${index * 100}ms, transform 0.5s ease ${index * 100}ms`,
              }}
            >
              <ExpenseCard expense={exp} />
            </div>
          ))}
        </section>
      </div>
    </div>
  );
}