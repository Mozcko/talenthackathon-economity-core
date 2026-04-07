// frontend/src/components/Dashboard.jsx
import { useAuth } from '@clerk/clerk-react';
import { useEffect, useState } from 'react';

export default function Dashboard() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(true);

  // Leemos la URL de la API desde las variables de entorno
  const API_URL = import.meta.env.PUBLIC_API_URL;

  useEffect(() => {
    async function obtenerResumen() {
      if (!isSignedIn) return;

      try {
        // 1. Obtenemos el JWT seguro de Clerk
        const token = await getToken();

        // 2. Hacemos la petición a tu API en FastAPI usando la variable de entorno
        const respuesta = await fetch(`${API_URL}/dashboard/summary`, {
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
  if (!isLoaded || cargando) return <div className="p-4 text-center">Cargando tus finanzas... ⏳</div>;
  if (error) return <div className="p-4 text-red-500">❌ Error: {error}</div>;
  if (!datos) return null;

  // --- Renderizado del Dashboard ---
  return (
    <div className="p-6 bg-white rounded-xl shadow-md space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Resumen Financiero</h2>
      
      {/* Tarjetas Principales */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
          <p className="text-sm text-blue-600 font-semibold">Saldo Total</p>
          <p className="text-3xl font-bold text-blue-900">${datos.saldo_total}</p>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg border border-green-100">
          <p className="text-sm text-green-600 font-semibold">Flujo de Caja Mensual</p>
          <p className="text-3xl font-bold text-green-900">${datos.flujo_caja_mensual}</p>
        </div>
        
        <div className="bg-purple-50 p-4 rounded-lg border border-purple-100">
          <p className="text-sm text-purple-600 font-semibold">Score de Resiliencia</p>
          <p className="text-3xl font-bold text-purple-900">{datos.score_resiliencia} / 850</p>
        </div>
      </div>

      {/* Meta y Oportunidad */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
        {datos.meta_proxima ? (
          <div className="border p-4 rounded-lg">
            <h3 className="font-bold text-gray-700">🎯 Próxima Meta: {datos.meta_proxima.nombre}</h3>
            <p className="text-gray-500 text-sm">Objetivo: ${datos.meta_proxima.monto_objetivo}</p>
            {/* Aquí podrías agregar una barra de progreso más adelante */}
          </div>
        ) : (
          <div className="border p-4 rounded-lg text-gray-500">
            <p>No tienes metas activas. ¡Crea una!</p>
          </div>
        )}

        {datos.mejor_oportunidad && (
          <div className="border p-4 rounded-lg bg-yellow-50 border-yellow-200">
            <h3 className="font-bold text-yellow-800">💡 Oportunidad Sugerida</h3>
            <p className="text-sm text-yellow-700">
              Invertir en <b>{datos.mejor_oportunidad.entidad}</b> ({datos.mejor_oportunidad.tipo}) 
              con tasa del <b>{(datos.mejor_oportunidad.tasa_rendimiento_actual * 100).toFixed(2)}%</b>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}