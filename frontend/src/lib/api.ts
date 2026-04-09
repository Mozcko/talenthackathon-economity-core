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

    // Check if user exists in the backend
    const userRes = await fetch(`/api/usuarios/${userId}`, { headers });

    let tenantId: string;
    let cuentaId: string;

    if (userRes.status === 404) {
      // New user — provision tenant → user → default account
      const tenantRes = await fetch('/api/organizaciones/', {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre: 'Personal', plan_suscripcion: 'gratis' }),
      });
      if (!tenantRes.ok) throw new Error(`Error al crear organización: ${tenantRes.status}`);
      tenantId = (await tenantRes.json()).id;

      const createUserRes = await fetch('/api/usuarios/', {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: userId, tenant_id: tenantId }),
      });
      if (!createUserRes.ok) throw new Error(`Error al registrar usuario: ${createUserRes.status}`);

      const cuentaRes = await fetch(`/api/usuarios/${userId}/cuentas/`, {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre: 'Efectivo', tipo: 'Efectivo', saldo_actual: 0, usuario_id: userId, tenant_id: tenantId }),
      });
      if (!cuentaRes.ok) throw new Error(`Error al crear cuenta: ${cuentaRes.status}`);
      cuentaId = (await cuentaRes.json()).id;

    } else if (userRes.ok) {
      tenantId = (await userRes.json()).tenant_id;

      const cuentasRes = await fetch(`/api/usuarios/${userId}/cuentas/`, { headers });
      if (!cuentasRes.ok) throw new Error(`Error cargando cuentas: ${cuentasRes.status}`);
      const cuentas = await cuentasRes.json();
      const first = Array.isArray(cuentas) ? cuentas[0] : undefined;

      if (!first) {
        // User exists but no accounts — create default
        const cuentaRes = await fetch(`/api/usuarios/${userId}/cuentas/`, {
          method: 'POST',
          headers: { ...headers, 'Content-Type': 'application/json' },
          body: JSON.stringify({ nombre: 'Efectivo', tipo: 'Efectivo', saldo_actual: 0, usuario_id: userId, tenant_id: tenantId }),
        });
        if (!cuentaRes.ok) throw new Error(`Error al crear cuenta: ${cuentaRes.status}`);
        cuentaId = (await cuentaRes.json()).id;
      } else {
        cuentaId = first.id;
      }
    } else {
      throw new Error(`Error cargando usuario: ${userRes.status}`);
    }

    const ctx: AppContext = { userId, cuentaId, tenantId };
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
