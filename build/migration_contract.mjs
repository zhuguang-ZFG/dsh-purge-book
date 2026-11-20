// Fake prompt objects only: never install plugins or call Apply/revert.
import assert from 'node:assert/strict';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

assert.equal(process.permission?.has('fs.write'), false);
assert.equal(process.permission?.has('child'), false);
const roots = process.argv.slice(2).map(p => path.resolve(p));
const modules = await Promise.all(roots.map(root => import(pathToFileURL(path.join(root, 'lib/identity.js')).href)));
const checks = [];
for (const order of [[0, 1], [1, 0]]) {
  const calls = [];
  const prompt = { async assemble() { return { sections: [], contexts: [], tools: [], variables: {} }; } };
  for (const index of order) {
    modules[index].installAssembleGuard(prompt, value => { calls.push(index); return value; });
    modules[index].installAssembleGuard(prompt, value => { calls.push(index); return value; });
  }
  await prompt.assemble();
  assert.deepEqual(calls, order);
  checks.push(`跨包顺序 ${order.join('→')}：每包内部幂等，两包改写均执行`);
}
console.log(JSON.stringify({ checks, scope: 'fake prompt; no host or model request' }));
