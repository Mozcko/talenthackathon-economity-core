import { useEffect, useState } from 'react';
import { apiFetch } from '../../../lib/api';

interface Perfil {
  usuario_id: string;
  total_xp: number;
  nivel_actual: string;
  racha_actual: number;
  racha_maxima: number;
  fecha_ultima_actividad: string | null;
  siguiente_nivel: string | null;
  xp_para_siguiente_nivel: number | null;
  porcentaje_progreso: number;
}

interface Logro {
  codigo_logro: string;
  desbloqueado_en: string;
  definicion: Record<string, any>;
}

interface Objetivo {
  mensaje: string;
  xp_objetivo: number | null;
  progreso: number;
  completado: boolean;
}

// Mock example for the Perfil interface. 
// You can pass this to useState<Perfil | null>(MOCK_PERFIL) to test the UI.
const MOCK_PERFIL: Perfil = {
  usuario_id: 'user_2N0xV8...',
  total_xp: 1250,
  nivel_actual: 'Plata',
  racha_actual: 5,
  racha_maxima: 12,
  fecha_ultima_actividad: new Date().toISOString(),
  siguiente_nivel: 'Oro',
  xp_para_siguiente_nivel: 250,
  porcentaje_progreso: 75,
};

// Mock example for the Objetivo interface to ensure a complete UI preview.
const MOCK_OBJETIVO: Objetivo = {
  mensaje: '¡Sigue así! Estás a punto de alcanzar tu meta de ahorro mensual.',
  xp_objetivo: 500,
  progreso: 0.85,
  completado: false,
};

export default function GamificationProfile() {
  const [perfil, setPerfil] = useState<Perfil | null>(MOCK_PERFIL);
  const [logros, setLogros] = useState<Logro[]>([]);
  const [Objetivo, setObjetivo] = useState<Objetivo | null>(MOCK_OBJETIVO);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // API logic is preserved but commented out to prioritize mock data as requested.
    /* Promise.allSettled([
      apiFetch<Perfil>('/gamification/profile'),
      apiFetch<Logro[]>('/gamification/achievements'),
      apiFetch<Objetivo>('/gamification/next-milestone'),
    ]).then(([p, a, h]) => {
      if (p.status === 'fulfilled') setPerfil(p.value);
      if (a.status === 'fulfilled') setLogros(a.value);
      if (h.status === 'fulfilled') setObjetivo(h.value);
      if (p.status === 'rejected' && a.status === 'rejected' && h.status === 'rejected') {
        setError(p.reason?.message ?? 'Error cargando perfil');
      }
    }).finally(() => setLoading(false));
    */
  }, []);

  if (loading) {
    return (
      <div className="p-6 md:p-8 space-y-4">
        {[1, 2, 3].map((i) => <div key={i} className="h-28 rounded-2xl bg-surface-container-high animate-pulse" />)}
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{error}</div>
      </div>
    );
  }

  const perfilDisplay: Perfil = perfil ?? {
    usuario_id: '',
    total_xp: 0,
    nivel_actual: 'bronze',
    racha_actual: 0,
    racha_maxima: 0,
    fecha_ultima_actividad: null,
    siguiente_nivel: 'silver',
    xp_para_siguiente_nivel: 100,
    porcentaje_progreso: 0,
  };

  return (
    <div className="p-6 md:p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-on-surface">Logros y Progreso</h1>
        <p className="text-on-surface/50 mt-1">Tu historial de gamificación financiera</p>
      </div>

      {/* Profile Card */}
      <div className="bg-primary-container rounded-2xl p-6 text-white space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white/60 text-sm font-medium uppercase tracking-wider">Nivel Actual</p>
            <p className="text-4xl font-black mt-1">{perfilDisplay.nivel_actual}</p>
            {perfilDisplay.siguiente_nivel && (
              <p className="text-white/50 text-sm mt-1">→ {perfilDisplay.siguiente_nivel}</p>
            )}
          </div>
          <div className="text-right">
            <p className="text-white/60 text-sm font-medium uppercase tracking-wider">XP Total</p>
            <p className="text-4xl font-black mt-1 text-on-tertiary-fixed">{perfilDisplay.total_xp.toLocaleString()}</p>
            {perfilDisplay.xp_para_siguiente_nivel !== null && (
              <p className="text-white/50 text-sm mt-1">{perfilDisplay.xp_para_siguiente_nivel} XP para subir</p>
            )}
          </div>
        </div>

        {/* XP Progress */}
        <div>
          <div className="flex justify-between text-xs text-white/50 mb-1">
            <span>Progreso al siguiente nivel</span>
            <span>{perfilDisplay.porcentaje_progreso.toFixed(0)}%</span>
          </div>
          <div className="w-full bg-white/10 h-3 rounded-full overflow-hidden">
            <div
              className="bg-on-tertiary-fixed h-full rounded-full transition-all duration-1000"
              style={{ width: `${perfilDisplay.porcentaje_progreso}%` }}
            />
          </div>
        </div>

        {/* Streaks */}
        <div className="grid grid-cols-2 gap-4 pt-2 border-t border-white/10">
          <div>
            <p className="text-white/60 text-xs font-medium uppercase tracking-wider">Racha Actual</p>
            <p className="text-2xl font-bold mt-1">🔥 {perfilDisplay.racha_actual} días</p>
          </div>
          <div>
            <p className="text-white/60 text-xs font-medium uppercase tracking-wider">Racha Máxima</p>
            <p className="text-2xl font-bold mt-1">⚡ {perfilDisplay.racha_maxima} días</p>
          </div>
        </div>
      </div>

      {/* Next Milestone */}
      {Objetivo && (
        <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-6 space-y-3">
          <div className="flex items-center gap-2">
            <span className="text-xl">{Objetivo.completado ? '✅' : '🎯'}</span>
            <h2 className="font-bold text-on-surface text-lg">Próximo Objetivo</h2>
          </div>
          <p className="text-on-surface/70">{Objetivo.mensaje}</p>
          {!Objetivo.completado && (
            <>
              <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                <div
                  className="bg-secondary h-full rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(100, Objetivo.progreso * 100)}%` }}
                />
              </div>
              <p className="text-xs text-on-surface/40">{(Objetivo.progreso * 100).toFixed(0)}% completado{Objetivo.xp_objetivo ? ` · ${Objetivo.xp_objetivo} XP objetivo` : ''}</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
