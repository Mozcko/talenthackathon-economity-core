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

interface Hito {
  mensaje: string;
  xp_objetivo: number | null;
  progreso: number;
  completado: boolean;
}

export default function GamificationProfile() {
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [logros, setLogros] = useState<Logro[]>([]);
  const [hito, setHito] = useState<Hito | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiFetch<Perfil>('/gamification/profile'),
      apiFetch<Logro[]>('/gamification/achievements'),
      apiFetch<Hito>('/gamification/next-milestone'),
    ])
      .then(([p, a, h]) => { setPerfil(p); setLogros(a); setHito(h); })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
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

  if (!perfil) return null;

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
            <p className="text-4xl font-black mt-1">{perfil.nivel_actual}</p>
            {perfil.siguiente_nivel && (
              <p className="text-white/50 text-sm mt-1">→ {perfil.siguiente_nivel}</p>
            )}
          </div>
          <div className="text-right">
            <p className="text-white/60 text-sm font-medium uppercase tracking-wider">XP Total</p>
            <p className="text-4xl font-black mt-1 text-on-tertiary-fixed">{perfil.total_xp.toLocaleString()}</p>
            {perfil.xp_para_siguiente_nivel !== null && (
              <p className="text-white/50 text-sm mt-1">{perfil.xp_para_siguiente_nivel} XP para subir</p>
            )}
          </div>
        </div>

        {/* XP Progress */}
        <div>
          <div className="flex justify-between text-xs text-white/50 mb-1">
            <span>Progreso al siguiente nivel</span>
            <span>{perfil.porcentaje_progreso.toFixed(0)}%</span>
          </div>
          <div className="w-full bg-white/10 h-3 rounded-full overflow-hidden">
            <div
              className="bg-on-tertiary-fixed h-full rounded-full transition-all duration-1000"
              style={{ width: `${perfil.porcentaje_progreso}%` }}
            />
          </div>
        </div>

        {/* Streaks */}
        <div className="grid grid-cols-2 gap-4 pt-2 border-t border-white/10">
          <div>
            <p className="text-white/60 text-xs font-medium uppercase tracking-wider">Racha Actual</p>
            <p className="text-2xl font-bold mt-1">🔥 {perfil.racha_actual} días</p>
          </div>
          <div>
            <p className="text-white/60 text-xs font-medium uppercase tracking-wider">Racha Máxima</p>
            <p className="text-2xl font-bold mt-1">⚡ {perfil.racha_maxima} días</p>
          </div>
        </div>
      </div>

      {/* Next Milestone */}
      {hito && (
        <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-6 space-y-3">
          <div className="flex items-center gap-2">
            <span className="text-xl">{hito.completado ? '✅' : '🎯'}</span>
            <h2 className="font-bold text-on-surface text-lg">Próximo Hito</h2>
          </div>
          <p className="text-on-surface/70">{hito.mensaje}</p>
          {!hito.completado && (
            <>
              <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                <div
                  className="bg-secondary h-full rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(100, hito.progreso * 100)}%` }}
                />
              </div>
              <p className="text-xs text-on-surface/40">{(hito.progreso * 100).toFixed(0)}% completado{hito.xp_objetivo ? ` · ${hito.xp_objetivo} XP objetivo` : ''}</p>
            </>
          )}
        </div>
      )}

      {/* Achievements */}
      <div>
        <h2 className="font-bold text-on-surface text-xl mb-4">Logros Desbloqueados ({logros.length})</h2>
        {logros.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-on-surface/30">
            <span className="text-5xl mb-3">🏆</span>
            <p className="italic">Completa acciones para desbloquear logros</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {logros.map((logro) => (
              <div key={logro.codigo_logro} className="flex items-start gap-4 p-4 rounded-2xl border border-outline-variant/30 bg-surface-container-lowest hover:shadow-sm transition-shadow">
                <div className="w-10 h-10 rounded-xl bg-secondary/10 flex items-center justify-center text-xl shrink-0">
                  {logro.definicion?.icono ?? '🏅'}
                </div>
                <div className="min-w-0">
                  <p className="font-bold text-on-surface text-sm truncate">
                    {logro.definicion?.nombre ?? logro.codigo_logro}
                  </p>
                  {logro.definicion?.descripcion && (
                    <p className="text-xs text-on-surface/50 mt-0.5 line-clamp-2">{logro.definicion.descripcion}</p>
                  )}
                  <p className="text-xs text-on-surface/30 mt-1">
                    {new Date(logro.desbloqueado_en).toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
