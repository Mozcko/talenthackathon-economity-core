import { useEffect, useState } from 'react';
import { apiFetch, getAppContext } from '../../../lib/api';

interface Transaccion {
  id: string;
  monto: string;
  descripcion: string | null;
  fecha_operacion: string;
  cuenta_id: string;
  sub_categoria_id: number;
  created_at: string;
}

function formatMXN(value: string) {
  return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(parseFloat(value));
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' });
}

export default function TransactionList() {
  const [transactions, setTransactions] = useState<Transaccion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const { cuentaId } = await getAppContext();
        const data = await apiFetch<Transaccion[]>(`/transacciones/cuenta/${cuentaId}`);
        setTransactions(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleDelete = async (id: string) => {
    setDeletingId(id);
    try {
      await apiFetch(`/transacciones/${id}`, { method: 'DELETE' });
      setTransactions((prev) => prev.filter((t) => t.id !== id));
    } catch (err: any) {
      alert(`Error al eliminar: ${err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-16 rounded-2xl bg-surface-container-high animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 flex items-center gap-2">
        <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        {error}
      </div>
    );
  }

  if (transactions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-on-surface/30">
        <svg className="w-12 h-12 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
        <p className="italic">No hay transacciones registradas</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {transactions.map((t) => {
        const monto = parseFloat(t.monto);
        const isNegative = monto < 0;
        return (
          <div
            key={t.id}
            className="flex items-center justify-between p-4 rounded-2xl border border-outline-variant/30 bg-surface-container-lowest hover:shadow-sm transition-shadow group"
          >
            <div className="flex items-center gap-4">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold ${isNegative ? 'bg-red-50 text-red-500' : 'bg-emerald-50 text-emerald-600'}`}>
                {isNegative ? '−' : '+'}
              </div>
              <div>
                <p className="font-semibold text-on-surface text-sm">
                  {t.descripcion ?? 'Sin descripción'}
                </p>
                <p className="text-xs text-on-surface/50 mt-0.5">{formatDate(t.fecha_operacion)}</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <span className={`text-lg font-extrabold ${isNegative ? 'text-red-500' : 'text-secondary'}`}>
                {formatMXN(t.monto)}
              </span>
              <button
                onClick={() => handleDelete(t.id)}
                disabled={deletingId === t.id}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-2 rounded-lg text-on-surface/30 hover:text-red-500 hover:bg-red-50 disabled:cursor-not-allowed"
                title="Eliminar transacción"
              >
                {deletingId === t.id
                  ? <svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v3m0 12v3m9-9h-3M6 12H3" /></svg>
                  : <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                }
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
