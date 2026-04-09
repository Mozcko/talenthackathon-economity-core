// Shared API utility — all components use these helpers

// Poll until Clerk has an active session (max 10s)
async function waitForClerkReady(): Promise<void> {
  const deadline = Date.now() + 10_000;
  while (Date.now() < deadline) {
    if ((window as any).Clerk?.session) return;
    await new Promise((r) => setTimeout(r, 50));
  }
  throw new Error('No hay sesión activa');
}

async function getAuthHeaders(): Promise<Record<string, string>> {
  await waitForClerkReady();
  const token = await (window as any).Clerk?.session?.getToken() as string | null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export interface AppContext {
  userId: string;
  cuentaId: string;
  tenantId: string;
}

// Module-level promise so concurrent callers share one in-flight request
let _ctxPromise: Promise<AppContext> | null = null;

export async function getAppContext(): Promise<AppContext> {
  if (_ctxPromise) return _ctxPromise;

  _ctxPromise = (async (): Promise<AppContext> => {
    const cached = sessionStorage.getItem('economity_ctx');
    if (cached) {
      try { return JSON.parse(cached); } catch { /* stale cache */ }
    }

    await waitForClerkReady();
    const userId = (window as any).Clerk?.user?.id as string;
    if (!userId) throw new Error('No hay sesión activa');

    const headers = await getAuthHeaders();
    const res = await fetch(`/api/usuarios/${userId}/cuentas/`, { headers });
    if (!res.ok) throw new Error(`Error cargando cuenta: ${res.status}`);

    const data = await res.json();
    const cuenta = Array.isArray(data) ? data[0] : data;

    const ctx: AppContext = { userId, cuentaId: cuenta.id, tenantId: cuenta.tenant_id };
    sessionStorage.setItem('economity_ctx', JSON.stringify(ctx));
    return ctx;
  })();

  // Reset so next call retries on failure
  _ctxPromise.catch(() => { _ctxPromise = null; });
  return _ctxPromise;
}

export async function apiFetch<T = any>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = await getAuthHeaders();
  const res = await fetch(`/api${path}`, {
    ...options,
    headers: {
      ...headers,
      ...(options.headers as Record<string, string> ?? {}),
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Error ${res.status}`);
  }
  return res.json();
}
