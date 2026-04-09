import type { APIRoute } from 'astro';

const BACKEND = (import.meta.env.PUBLIC_API_URL as string).replace(/\/$/, '');

export const ALL: APIRoute = async ({ request, params }) => {
  const path = params.path ?? '';
  const search = new URL(request.url).search;
  const target = `${BACKEND}/${path}${search}`;

  const headers = new Headers(request.headers);
  headers.delete('host');

  const init: RequestInit = { method: request.method, headers };

  if (request.method !== 'GET' && request.method !== 'HEAD') {
    init.body = await request.arrayBuffer();
  }

  const upstream = await fetch(target, init);

  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: upstream.headers,
  });
};
