import type { APIRoute } from 'astro';

export const ALL: APIRoute = async ({ request, params }) => {
  // Read at request time (runtime) so Railway env vars are picked up
  const rawUrl =
    (import.meta.env.PUBLIC_API_URL as string | undefined) ||
    (process.env.PUBLIC_API_URL as string | undefined) ||
    '';

  if (!rawUrl) {
    return new Response(
      JSON.stringify({ detail: 'Backend URL not configured — set PUBLIC_API_URL in Railway' }),
      { status: 503, headers: { 'Content-Type': 'application/json' } }
    );
  }

  const BACKEND = rawUrl.replace(/\/$/, '');
  const path = params.path ?? '';
  const search = new URL(request.url).search;
  const target = `${BACKEND}/${path}${search}`;

  const headers = new Headers(request.headers);
  headers.delete('host');

  const init: RequestInit = { method: request.method, headers };

  if (request.method !== 'GET' && request.method !== 'HEAD') {
    init.body = await request.arrayBuffer();
  }

  try {
    const upstream = await fetch(target, init);
    return new Response(upstream.body, {
      status: upstream.status,
      statusText: upstream.statusText,
      headers: upstream.headers,
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    return new Response(
      JSON.stringify({ detail: `Proxy fetch failed: ${msg} (target: ${target})` }),
      { status: 502, headers: { 'Content-Type': 'application/json' } }
    );
  }
};
