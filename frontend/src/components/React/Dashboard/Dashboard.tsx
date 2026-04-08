// frontend/src/components/Dashboard.jsx
import { ClerkProvider, useAuth } from '@clerk/react';
import { useEffect, useState } from 'react';

function DashboardSkeleton() {
  return (
    <div className="card-base h-full flex flex-col justify-center space-y-8 shadow-(--shadow-ambient) bg-primary-container animate-pulse">
      <div className="flex justify-between items-center border-b border-white/10 pb-6">
        <div className="space-y-3">
          <div className="h-4 w-24 bg-white/10 rounded"></div>
          <div className="h-10 w-48 bg-white/10 rounded"></div>
        </div>
        <div className="flex flex-col items-end space-y-3">
          <div className="h-4 w-28 bg-white/10 rounded"></div>
          <div className="h-8 w-16 bg-white/10 rounded-lg"></div>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-6 pt-2">
        {[1, 2].map((i) => (
          <div key={i} className="space-y-3">
            <div className="h-4 w-32 bg-white/10 rounded"></div>
            <div className="h-8 w-36 bg-white/10 rounded"></div>
          </div>
        ))}
      </div>
    </div>
  );
}

function DashboardContent() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(true);

  // Usamos la variable de entorno, o el proxy '/api' por defecto para entorno local
  const API_URL = import.meta.env.PUBLIC_API_URL || '/api';

  useEffect(() => {
    async function obtenerResumen() {
      if (!isSignedIn) return;

      try {
        // 1. Obtenemos el JWT seguro de Clerk
        const token = await getToken();

        const fetchUrl = `${API_URL}/dashboard/summary`;
        console.log("🔍 [DEBUG] Obteniendo resumen desde URL:", fetchUrl);

        // 2. Hacemos la petición a tu API en FastAPI usando la variable de entorno
        /* --- COMENTADO TEMPORALMENTE PARA USAR MOCK ---
        const respuesta = await fetch(fetchUrl, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!respuesta.ok) {
          throw new Error(`Error del servidor: ${respuesta.status}`);
        }

        const data = await respuesta.json();
        setDatos(data);
        ------------------------------------------------ */

        // --- MOCK DATA ---
        await new Promise(resolve => setTimeout(resolve, 800)); // Simulamos carga de red
        setDatos({
          saldo_total: "15,340",
          crecimiento_porcentaje: 12.5,
          score_resiliencia: 65,
          flujo_caja_mensual: "1,500",
          fondo_emergencia_porcentaje: 85
        });
      } catch (err) {
        console.error("Error cargando dashboard:", err);
        setError(err.message);
      } finally {
        setCargando(false);
      }
    }

    if (isLoaded) {
      obtenerResumen();
    }
  }, [isLoaded, isSignedIn, getToken]);

  // --- Estados de carga y error ---
  if (!isLoaded || cargando) return <DashboardSkeleton />;
  
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

  // --- Renderizado del Dashboard ---
  return (
    <div className="card-base h-full flex flex-col justify-center space-y-8 shadow-(--shadow-ambient) bg-primary-container">
      {/* Top: Assets & Score */}
      <div className="flex justify-between items-center border-b border-white/10 pb-6">
        <div>
          <p className="text-sm font-medium text-white/60 mb-1">Patrimonio Total</p>
          <div className="flex items-baseline gap-2">
            <h2 className="text-display-lg font-bold text-white">
              ${datos.saldo_total}
            </h2>
            <span className="text-lg font-medium text-white/60">MXN</span>
          </div>
          <p className="text-sm font-medium text-on-tertiary-fixed mt-1 flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            +{datos.crecimiento_porcentaje}% este mes
          </p>
        </div>
        <div className="text-right flex flex-col items-end">
          <p className="text-sm font-medium text-white/60 mb-2">Score Resiliencia</p>
          <div className="ai-chip text-lg px-4 py-2">
            {datos.score_resiliencia}
          </div>
        </div>
      </div>

      {/* Bottom: Cashflow & Emergency Fund */}
      <div className="grid grid-cols-2 gap-6 pt-2">
        <div>
          <p className="text-sm font-medium text-white/60 mb-1">Flujo Libre</p>
          <p className="text-3xl font-bold text-on-tertiary-fixed">
            ${datos.flujo_caja_mensual}
          </p>
        </div>
        <div>
          <p className="text-sm font-medium text-white/60 mb-1">Fondo de Emergencia</p>
          <div className="flex items-end gap-2 mb-2">
            <p className="text-3xl font-bold text-white">
              {datos.fondo_emergencia_porcentaje}%
            </p>
            <p className="text-sm font-medium text-white/60 pb-1">completado</p>
          </div>
          <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden">
            <div className="bg-secondary h-full rounded-full transition-all duration-1000 ease-out" style={{ width: `${datos.fondo_emergencia_porcentaje}%` }}></div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  return (
    <ClerkProvider publishableKey={import.meta.env.PUBLIC_CLERK_PUBLISHABLE_KEY}>
      <DashboardContent />
    </ClerkProvider>
  );
}