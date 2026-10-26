const REPO = 'maverikhe-cpu/kindle-tuen-mun-calendar';
const MANIFEST = 'https://maverikhe-cpu.github.io/kindle-tuen-mun-calendar/manifest.json';
export async function checkAndRefresh(env, request = fetch, now = Date.now()) {
  const headers = { Authorization: `Bearer ${env.GITHUB_TOKEN}`, Accept: 'application/vnd.github+json', 'User-Agent': 'kindle-calendar-scheduler', 'X-GitHub-Api-Version': '2022-11-28' };
  async function api(path, options = {}) {
    const response = await request(`https://api.github.com/repos/${REPO}${path}`, { ...options, headers, signal: AbortSignal.timeout(20000) });
    if (!response.ok) throw new Error(`GitHub ${response.status} for ${path}`);
    return response.status === 204 ? null : response.json();
  }
  let generatedAt = 0;
  try {
    const response = await request(`${MANIFEST}?check=${now}`, { cache: 'no-store', signal: AbortSignal.timeout(15000) });
    if (!response.ok) throw new Error(`Manifest ${response.status}`);
    const manifest = await response.json();
    if (Number.isFinite(manifest.generatedAt) && manifest.generatedAt <= now + 300000) generatedAt = manifest.generatedAt;
  } catch { /* Missing or unavailable manifest should trigger recovery. */ }
  if (generatedAt && now - generatedAt < 25 * 60000) return { action: 'fresh', generatedAt };
  const runs = await api('/actions/workflows/calendar.yml/runs?per_page=10');
  if (runs.workflow_runs.some(run => run.status !== 'completed')) return { action: 'already-running' };
  await api('/actions/workflows/calendar.yml/dispatches', { method: 'POST', body: JSON.stringify({ ref: 'main' }) });
  return { action: 'dispatched', previousGeneratedAt: generatedAt };
}
export default {
  async scheduled(controller, env) {
    const result = await checkAndRefresh(env);
    console.log(JSON.stringify({ scheduledTime: controller.scheduledTime, ...result }));
  },
  fetch() { return new Response('Kindle calendar scheduler: cloud cron checks every 5 minutes.\n'); }
};
