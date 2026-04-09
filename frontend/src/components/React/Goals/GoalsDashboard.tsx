import { useEffect, useState } from 'react';
import { apiFetch, getAppContext } from '../../../lib/api';

interface Meta {
  id: string;
  nombre: string;
  monto_objetivo: string;
  progreso_actual: string;
  fecha_limite: string | null;
  usuario_id: string;
  created_at: string;
}

function formatMXN(value: string) {
  return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(parseFloat(value));
}

function ProgressBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
      <div
        className="bg-secondary h-full rounded-full transition-all duration-700"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

export default function GoalsDashboard() {
  const [metas, setMetas] = useState<Meta[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [progressModal, setProgressModal] = useState<Meta | null>(null);
  const [progressAmount, setProgressAmount] = useState('');
  const [savingProgress, setSavingProgress] = useState(false);

  // Create form state
  const [form, setForm] = useState({ nombre: '', monto_objetivo: '', fecha_limite: '' });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    apiFetch<Meta[]>('/metas/')
      .then(setMetas)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const { userId, tenantId } = await getAppContext();
      const nueva = await apiFetch<Meta>('/metas/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nombre: form.nombre,
          monto_objetivo: parseFloat(form.monto_objetivo),
          progreso_actual: 0,
          fecha_limite: form.fecha_limite || null,
          usuario_id: userId,
          tenant_id: tenantId,
        }),
      });
      setMetas((prev) => [nueva, ...prev]);
      setForm({ nombre: '', monto_objetivo: '', fecha_limite: '' });
      setShowForm(false);
    } catch (err: any) {
      alert(`Error al crear: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    setDeletingId(id);
    try {
      await apiFetch(`/metas/${id}`, { method: 'DELETE' });
      setMetas((prev) => prev.filter((m) => m.id !== id));
    } catch (err: any) {
      alert(`Error al eliminar: ${err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  const handleAddProgress = async () => {
    if (!progressModal || !progressAmount) return;
    setSavingProgress(true);
    try {
      const updated = await apiFetch<Meta>(
        `/metas/${progressModal.id}/progreso?monto_a_sumar=${parseFloat(progressAmount)}`,
        { method: 'PATCH' }
      );
      setMetas((prev) => prev.map((m) => (m.id === updated.id ? updated : m)));
      setProgressModal(null);
      setProgressAmount('');
    } catch (err: any) {
      alert(`Error al actualizar progreso: ${err.message}`);
    } finally {
      setSavingProgress(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4 p-6">
        {[1, 2, 3].map((i) => <div key={i} className="h-24 rounded-2xl bg-surface-container-high animate-pulse" />)}
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-on-surface">Mis Metas</h1>
          <p className="text-on-surface/50 mt-1">Rastrea tu progreso hacia tus objetivos financieros</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary text-sm px-5 py-2.5 flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
          Nueva Meta
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{error}</div>
      )}

      {/* Create Form */}
      {showForm && (
        <form onSubmit={handleCreate} className="card-base space-y-4 border border-outline-variant/30">
          <h2 className="font-bold text-lg text-on-surface">Nueva Meta Financiera</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-on-surface/60 mb-1 block">Nombre</label>
              <input
                className="input-field border border-outline-variant/30"
                placeholder="Ej: Fondo de emergencia"
                value={form.nombre}
                onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium text-on-surface/60 mb-1 block">Monto objetivo (MXN)</label>
              <input
                type="number"
                min="1"
                step="0.01"
                className="input-field border border-outline-variant/30"
                placeholder="50000"
                value={form.monto_objetivo}
                onChange={(e) => setForm((f) => ({ ...f, monto_objetivo: e.target.value }))}
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium text-on-surface/60 mb-1 block">Fecha límite (opcional)</label>
              <input
                type="date"
                className="input-field border border-outline-variant/30"
                value={form.fecha_limite}
                onChange={(e) => setForm((f) => ({ ...f, fecha_limite: e.target.value }))}
              />
            </div>
          </div>
          <div className="flex gap-3 justify-end">
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary text-sm px-5 py-2">Cancelar</button>
            <button type="submit" disabled={saving} className="btn-primary text-sm px-5 py-2">
              {saving ? 'Guardando...' : 'Crear Meta'}
            </button>
          </div>
        </form>
      )}

      {/* Goals List */}
      {metas.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-on-surface/30">
          <svg className="w-14 h-14 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
          <p className="italic">Aún no tienes metas. ¡Crea tu primera!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {metas.map((meta) => {
            const objetivo = parseFloat(meta.monto_objetivo);
            const progreso = parseFloat(meta.progreso_actual);
            const pct = objetivo > 0 ? Math.min(100, (progreso / objetivo) * 100) : 0;
            return (
              <div key={meta.id} className="bg-surface-container-lowest rounded-2xl border border-outline-variant/30 p-6 space-y-4 hover:shadow-sm transition-shadow group">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-bold text-on-surface text-lg leading-tight">{meta.nombre}</h3>
                  <button
                    onClick={() => handleDelete(meta.id)}
                    disabled={deletingId === meta.id}
                    className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-lg text-on-surface/30 hover:text-red-500 hover:bg-red-50 shrink-0"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  </button>
                </div>

                <div className="flex items-end justify-between text-sm">
                  <span className="text-on-surface/50">Progreso</span>
                  <span className="font-bold text-secondary">{formatMXN(meta.progreso_actual)} / {formatMXN(meta.monto_objetivo)}</span>
                </div>

                <ProgressBar value={progreso} max={objetivo} />

                <div className="flex items-center justify-between">
                  <span className="text-xs text-on-surface/40">
                    {pct.toFixed(0)}% completado
                    {meta.fecha_limite && ` · Límite: ${new Date(meta.fecha_limite).toLocaleDateString('es-MX')}`}
                  </span>
                  <button
                    onClick={() => { setProgressModal(meta); setProgressAmount(''); }}
                    className="text-xs font-bold text-secondary hover:underline"
                  >
                    + Agregar progreso
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Progress Modal */}
      {progressModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-surface-container-lowest rounded-2xl p-6 w-full max-w-sm space-y-4 shadow-xl">
            <h3 className="font-bold text-lg text-on-surface">Agregar progreso</h3>
            <p className="text-sm text-on-surface/60">Meta: <span className="font-medium text-on-surface">{progressModal.nombre}</span></p>
            <input
              type="number"
              min="1"
              step="0.01"
              className="input-field border border-outline-variant/30 w-full"
              placeholder="Monto a agregar (MXN)"
              value={progressAmount}
              onChange={(e) => setProgressAmount(e.target.value)}
              autoFocus
            />
            <div className="flex gap-3 justify-end">
              <button onClick={() => setProgressModal(null)} className="btn-secondary text-sm px-4 py-2">Cancelar</button>
              <button
                onClick={handleAddProgress}
                disabled={!progressAmount || savingProgress}
                className="btn-primary text-sm px-4 py-2"
              >
                {savingProgress ? 'Guardando...' : 'Confirmar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
