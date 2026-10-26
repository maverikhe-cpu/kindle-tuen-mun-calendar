import { test } from 'node:test';
import assert from 'node:assert/strict';
import { checkAndRefresh } from './worker.mjs';
const now = 1793000000000;
for (const scenario of [
  { name: 'fresh image skips GitHub', age: 10, runs: [], action: 'fresh', count: 1 },
  { name: 'stale image dispatches', age: 40, runs: [], action: 'dispatched', count: 3 },
  { name: 'running job prevents duplicate', age: 40, runs: [{status:'in_progress'}], action:'already-running', count:2 },
  { name: 'unavailable image recovers', age: null, runs: [], action:'dispatched', count:3 },
]) test(scenario.name, async () => {
  let calls = [];
  const mock = async (url, options) => {
    calls.push(url);
    if (url.includes('manifest.json')) return scenario.age === null ? new Response('', {status:503}) : Response.json({generatedAt:now-scenario.age*60000});
    assert.equal(options.headers.Authorization, 'Bearer test');
    if (url.includes('/runs?')) return Response.json({workflow_runs:scenario.runs});
    assert.equal(options.method, 'POST');
    assert.deepEqual(JSON.parse(options.body), {ref:'main'});
    return new Response(null, {status:204});
  };
  assert.equal((await checkAndRefresh({GITHUB_TOKEN:'test'}, mock, now)).action, scenario.action);
  assert.equal(calls.length, scenario.count);
});
test('GitHub rejection is reported as failure', async () => {
  await assert.rejects(checkAndRefresh({GITHUB_TOKEN:'test'}, async url => url.includes('manifest') ? Response.json({generatedAt:1}) : new Response('', {status:401}), now), /GitHub 401/);
});
