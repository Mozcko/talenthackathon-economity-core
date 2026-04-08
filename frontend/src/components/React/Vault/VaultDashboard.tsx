import { useState, useEffect } from 'react';
import SummaryCard from './SummaryCard';
import AssetDistributionChart from './AssetDistributionChart';
import InvestmentCard from './InvestmentCard';

// Mock Data estricto según los requerimientos
const mockDashboard = { saldo_total: 124500.50, score_resiliencia: 720 };
const mockPortafolio = [
  { id: 1, entidad: "Nu México", tipo: "SOFIPO - Liquidez", monto: 45000.00, tasa: 0.145 },
  { id: 2, entidad: "CetesDirecto", tipo: "Gubernamental - Renta Fija", monto: 50000.00, tasa: 0.11 },
  { id: 3, entidad: "Finsus", tipo: "SOFIPO - Plazo Fijo", monto: 29500.50, tasa: 0.15 }
];

export default function VaultDashboard() {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<{ saldo_total: number; score_resiliencia: number } | null>(null);
  const [portfolioData, setPortfolioData] = useState<any[]>([]);

  // Simulación de carga de 1 segundo
  useEffect(() => {
    const timer = setTimeout(() => {
      setDashboardData(mockDashboard);
      setPortfolioData(mockPortafolio);
      setLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!dashboardData) return null;

  return (
    <div className="m-5 ml-5 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      <header>
        <h1 className="text-3xl font-bold text-gray-800 tracking-tight">Mi Vault</h1>
        <p className="text-gray-500 mt-1">Centro de Mando Patrimonial</p>
      </header>

      {/* Top: Tarjetas de resumen */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <SummaryCard
          title="Saldo Total"
          value={new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(dashboardData.saldo_total)}
          subtitle="Patrimonio invertido actual"
          trend="+5.2% este mes"
        />
        <SummaryCard
          title="Score de Resiliencia"
          value={dashboardData.score_resiliencia.toString()}
          subtitle="Salud e inmunidad financiera"
          trend="Excelente"
        />
      </section>

      {/* Middle & Bottom: Gráfica y Lista de Inversiones */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <section className="lg:col-span-1 bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col">
          <h2 className="text-xl font-bold text-gray-800 mb-6">Distribución de Activos</h2>
          <div className="flex-1 flex items-center justify-center min-h-[300px]">
            <AssetDistributionChart data={portfolioData} />
          </div>
        </section>

        <section className="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col space-y-4">
          <h2 className="text-xl font-bold text-gray-800 mb-2">Portafolio de Inversiones</h2>
          {portfolioData.map((inv) => (
            <InvestmentCard key={inv.id} investment={inv} />
          ))}
        </section>
      </div>
    </div>
  );
}