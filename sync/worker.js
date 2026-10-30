// Shared state for natochi.cv/boston. One JSON blob in KV, read and written by every phone.
const KEY = 'boston:state:v1';
const PATH = '/s/k7v2q9';
const ORIGINS = ['https://ignaciobernardo.github.io', 'https://natochi.cv', 'http://localhost:5191'];

function cors(req) {
  const o = req.headers.get('Origin') || '';
  const h = {
    'Access-Control-Allow-Methods': 'GET, PUT, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Cache-Control': 'no-store',
  };
  if (ORIGINS.includes(o)) h['Access-Control-Allow-Origin'] = o;
  return h;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const h = cors(request);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: h });
    if (url.pathname !== PATH) return new Response('not found', { status: 404, headers: h });
    if (request.method === 'GET') {
      const v = await env.KV.get(KEY);
      return new Response(v || 'null', { status: 200, headers: { ...h, 'Content-Type': 'application/json' } });
    }
    if (request.method === 'PUT') {
      const text = await request.text();
      if (text.length > 300000) return new Response('too big', { status: 413, headers: h });
      let body;
      try { body = JSON.parse(text); } catch (e) { return new Response('bad json', { status: 400, headers: h }); }
      if (!body || typeof body !== 'object' || !Array.isArray(body.addedStops)) {
        return new Response('bad state', { status: 400, headers: h });
      }
      await env.KV.put(KEY, text);
      return new Response('ok', { status: 200, headers: h });
    }
    return new Response('method', { status: 405, headers: h });
  },
};
