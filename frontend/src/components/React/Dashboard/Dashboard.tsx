import { useEffect, useState } from 'react';
import { apiFetch } from '../../../lib/api';

interface MetaProxima {
  nombre: string;
  monto_objetivo: string;
  progreso_actual: string;
  fecha_limite: string | null;
}

interface DashboardData {
  saldo_total: string;
  flujo_caja_mensual: string;
  score_resiliencia: number;
  meta_proxima: MetaProxima | null;
  mejor_oportunidad: Record<string, any> | null;
}

function Skeleton() {
  return (
    <div className="card-base h-full flex flex-col justify-center space-y-8 shadow-(--shadow-ambient) bg-primary-container animate-pulse">
      <div className="flex justify-between items-center border-b border-white/10 pb-6">
        <div className="space-y-3">
          <div className="h-4 w-24 bg-white/10 rounded" />
          <div className="h-10 w-48 bg-white/10 rounded" />
        </div>
        <div className="flex flex-col items-end space-y-3">
          <div className="h-4 w-28 bg-white/10 rounded" />
          <div className="h-8 w-16 bg-white/10 rounded-lg" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-6 pt-2">
        {[1, 2].map((i) => (
          <div key={i} className="space-y-3">
            <div className="h-4 w-32 bg-white/10 rounded" />
            <div className="h-8 w-36 bg-white/10 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [datos, setDatos] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    apiFetch<DashboardData>('/dashboard/summary')
      .then(setDatos)
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false));
  }, []);

  if (cargando) return <Skeleton />;

  if (error) {
    return (
      <div className="card-base h-full flex flex-col items-center justify-center text-center space-y-4 shadow-(--shadow-ambient) bg-primary-container text-white">
        <svg className="w-12 h-12 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="font-medium">No pudimos cargar tus datos.</p>
        <p className="text-sm text-white/60">{error}</p>
      </div>
    );
  }

  if (!datos) return null;

  const progresoPct = datos.meta_proxima
    ? Math.min(100, (parseFloat(datos.meta_proxima.progreso_actual) / parseFloat(datos.meta_proxima.monto_objetivo)) * 100)
    : 0;

  return (
    <div className="card-base h-full flex flex-col justify-center space-y-8 shadow-(--shadow-ambient) bg-primary-container">
      {/* Top: Assets & Score */}
      <div className="flex justify-between items-center border-b border-white/10 pb-6">
        <div>
          <p className="text-sm font-medium text-white/60 mb-1">Patrimonio Total</p>
          <div className="flex items-baseline gap-2">
            <h2 className="text-display-lg font-bold text-white">${datos.saldo_total}</h2>
            <span className="text-lg font-medium text-white/60">MXN</span>
          </div>
        </div>
        <div className="text-right flex flex-col items-end">
          <p className="text-sm font-medium text-white/60 mb-2">Score Resiliencia</p>
          <div className="ai-chip text-lg px-4 py-2">{datos.score_resiliencia}</div>
        </div>
      </div>

      {/* Bottom: Cashflow & Next Goal */}
      <div className="grid grid-cols-2 gap-6 pt-2">
        <div>
          <p className="text-sm font-medium text-white/60 mb-1">Flujo Libre Mensual</p>
          <p className="text-3xl font-bold text-on-tertiary-fixed">${datos.flujo_caja_mensual}</p>
        </div>

        <div>
          {datos.meta_proxima ? (
            <>
              <p className="text-sm font-medium text-white/60 mb-1">Meta Próxima</p>
              <p className="text-base font-bold text-white truncate">{datos.meta_proxima.nombre}</p>
              <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden mt-2">
                <div
                  className="bg-secondary h-full rounded-full transition-all duration-1000 ease-out"
                  style={{ width: `${progresoPct}%` }}
                />
              </div>
              <p className="text-xs text-white/50 mt-1">{progresoPct.toFixed(0)}% completado</p>
            </>
          ) : (
            <>
              <p className="text-sm font-medium text-white/60 mb-1">Meta Próxima</p>
              <p className="text-sm text-white/40 italic">Sin metas activas</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
