// 离线教学实验：只调用纯函数或假会话，不运行宿主、补丁写盘或网络工具。
import assert from 'node:assert/strict';
import path from 'node:path';
import { writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const root = path.resolve(process.argv[2]);
const packageName = process.argv[3] || 'dsh-purge-safe';
const moduleAt = (name) => import(pathToFileURL(path.join(root, name)).href);
const core = await moduleAt('lib/core.js');
const identity = await moduleAt('lib/identity.js');
const team = await moduleAt('lib/redteam/team-mode.js');
const retry = await moduleAt('lib/continue-retry.js');
const checks = [];
function check(name, fn) {
  fn();
  checks.push(name);
}

check('实验权限：写盘与子进程均被运行时拒绝', () => {
  assert.equal(process.permission?.has('fs.write'), false);
  assert.equal(process.permission?.has('child'), false);
  assert.throws(() => writeFileSync(path.join(process.env.DSH_HOME, 'denied.txt'), 'fixture'),
    { code: 'ERR_ACCESS_DENIED' });
  assert.throws(() => spawnSync(process.execPath, ['--version']), { code: 'ERR_ACCESS_DENIED' });
});

check('补丁集合：59 条、id 唯一、最大 96', () => {
  assert.equal(core.ALL_PATCHES.length, 59);
  assert.equal(new Set(core.ALL_PATCHES.map((p) => p.id)).size, 59);
  assert.equal(Math.max(...core.ALL_PATCHES.map((p) => p.id)), 96);
});

check('展示分组不丢定义：全部 applied 时折叠为 55 行', () => {
  const status = Object.fromEntries(core.ALL_PATCHES.map((p) => [p.id, 'applied']));
  const rows = core.groupPatchesForDisplay(core.ALL_PATCHES, status, 'web');
  assert.equal(rows.length, 55);
  assert.equal(rows.flatMap((row) => row.ids).length, 59);
  assert.deepEqual(core.PATCH_DISPLAY_GROUPS.approval_sentence, [5, 11, 12]);
});

check('ready 与严格判定：普通缺文件可就绪，关键 skipped 不可', () => {
  assert.equal(core.patchStatusReady('missing_file', {}), true);
  assert.equal(core.patchStatusReady('na', {}), false);
  assert.equal(core.patchStatusReady('skipped', { hostCleanGate: true }), false);
  assert.equal(core.isPatchResultSoftOk({ status: 'backup_failed' }, { optional: true }), false);
  assert.equal(core.isPatchResultSoftOk({ status: 'pattern_not_found' }, { optional: true }), true);
  assert.equal(core.isPatchResultSoftOk({ status: 'pattern_not_found' }, { strictFiles: true, optional: true }), false);
});

const inject = 'BOOK_CONTRACT_SENTINEL: local fixture only.';
const fixture = {
  sections: [
    { name: 'harness:identity', text: 'You are an AI agent powered by DeepSeek Harness.' },
    { name: 'deployment:persona-prefix', text: 'Retained fixture instructions.' },
    { name: packageName, text: inject },
    { name: 'workspace:baseline', text: 'No workspace instructions are currently active' },
  ],
  contexts: [
    { name: 'approval:policy', text: 'fixture removable' },
    { name: 'sandbox:policy', text: 'fixture required', required: true },
    { name: 'working-directory:current', text: 'Working directory: {{cwd}}.', required: true },
  ],
  tools: [{ name: 'fixture_read' }],
  variables: {},
};
const original = JSON.stringify(fixture);
const opts = {
  fallbackInject: inject,
  dropMnemon: false,
  dropWorkspaceBaseline: true,
  cwd: '/book-fixture',
  anchorText: 'BOOK_FIXTURE_ANCHOR',
};
const output = identity.rewritePromptAssembly(fixture, opts);

check('组装：完整正文折入 -100000 前缀，输入不变、工具保留', () => {
  assert.equal(JSON.stringify(fixture), original);
  assert.notEqual(output, fixture);
  assert.equal(output.sections[0].name, 'deployment:persona-prefix');
  assert.equal(output.sections[0].order, -100000);
  assert.ok(output.sections[0].text.startsWith(inject));
  assert.ok(!output.sections.some((s) => s.name === 'harness:identity' || s.name === 'workspace:baseline'));
  assert.equal(output.sections.reduce((n, s) => n + (String(s.text).split(inject).length - 1), 0), 1);
  assert.deepEqual(output.tools, fixture.tools);
});

check('最终尾段：能力协议 99999、锚点 100000 且最后', () => {
  assert.ok(output.sections.some((s) => s.name === identity.CAPABILITY_SECTION && s.order === 99999));
  assert.equal(output.sections.at(-1).name, packageName + ':anchor');
  assert.equal(output.sections.at(-1).order, 100000);
});

check('动态上下文：移除非 required 策略，保留 required 并填 cwd', () => {
  assert.ok(!output.contexts.some((c) => c.name === 'approval:policy'));
  assert.ok(output.contexts.some((c) => c.name === 'sandbox:policy' && c.required === true));
  assert.equal(output.contexts.find((c) => c.name === 'working-directory:current').text, 'Working directory: /book-fixture.');
  assert.equal(output.variables.cwd, '/book-fixture');
});

check('重复组装：全文仍在且不重复前缀', () => {
  const twice = identity.rewritePromptAssembly(output, opts);
  assert.equal(twice.sections.reduce((n, s) => n + (String(s.text).split(inject).length - 1), 0), 1);
});

check('红队叶子：保留执行角色，移除指挥稿和团队说明', () => {
  const child = identity.rewritePromptAssembly({
    sections: [
      { name: 'redteam:ops', text: '## 运行环境前提\nfixture dispatch procedure' },
      { name: 'team:policy', text: 'Agent Teams is available; fixture lead policy' },
    ],
    contexts: [], tools: [], variables: {},
  }, {
    fallbackInject: inject, dropMnemon: false, roleText: 'BOOK_EXECUTOR_ROLE',
    context: { session: { header: { origin: 'subagent', delegationDepth: 1, agentPreset: 'redteam' } } },
  });
  assert.ok(child.sections.some((s) => s.text === 'BOOK_EXECUTOR_ROLE'));
  assert.ok(!child.sections.some((s) => s.name === 'team:policy' || String(s.text).includes('fixture dispatch procedure')));
});

const prompt = { async assemble() { return { sections: [], contexts: [], tools: [], variables: {} }; } };
identity.installAssembleGuard(prompt, (assembled) => ({ ...assembled, fixtureRevision: 1 }));
const wrapped = prompt.assemble;
identity.installAssembleGuard(prompt, (assembled) => ({ ...assembled, fixtureRevision: 2 }));
assert.equal(prompt.assemble, wrapped);
assert.equal((await prompt.assemble()).fixtureRevision, 2);
prompt.assemble = async () => ({ sections: [], contexts: [], tools: [], variables: {}, replacement: true });
assert.equal((await prompt.assemble()).replacement, true);
assert.equal((await prompt.assemble()).fixtureRevision, 2);
checks.push('防重入：重复安装只换 slot；后续 setter 仍包装一次');

const originalFailure = { async assemble() { throw new Error('fixture assemble failure'); } };
identity.installAssembleGuard(originalFailure, value => ({ ...value, fallbackObserved: true }));
const recovered = await originalFailure.assemble();
assert.equal(recovered.fallbackObserved, true);
assert.deepEqual(recovered.sections, []);
assert.deepEqual(recovered.tools, []);
checks.push('原 assemble 抛错：空结构仍改写，但工具与上下文不代表完整');

const untouched = { sections: [{ name: 'fixture-kept', text: 'kept' }], tools: ['fixture-tool'] };
const rewriteFailure = { async assemble() { return untouched; } };
identity.installAssembleGuard(rewriteFailure, () => { throw new Error('fixture rewrite failure'); });
assert.equal(await rewriteFailure.assemble(), untouched);
checks.push('rewrite 抛错：返回原 assembled 对象，不伪报注入成功');

function session(header = {}, events = []) {
  return { header, events: [...events], append(type, data) { this.events.push({ type, data }); } };
}
check('团队：只开红队根会话一次，尊重已关闭事件', () => {
  const rootSession = session({ agentPreset: 'redteam', delegationDepth: 0, parentSession: 'old-history' });
  assert.equal(team.ensureRedteamTeamMode(rootSession), 'enabled');
  assert.equal(team.ensureRedteamTeamMode(rootSession), 'skip-already');
  assert.equal(rootSession.events.length, 1);
  const disabled = session({ agentPreset: 'redteam' }, [{ type: 'team/mode', data: { enabled: false } }]);
  assert.equal(team.ensureRedteamTeamMode(disabled), 'skip-already');
  assert.equal(disabled.events[0].data.enabled, false);
  const leaf = session({ agentPreset: 'redteam', origin: 'subagent', delegationDepth: 1 });
  assert.equal(team.ensureRedteamTeamMode(leaf), 'skip-not-root');
  assert.equal(leaf.events.length, 0);
});

check('中途切预设：standard 不永久封存，后续红队能启用', () => {
  const switched = session({ agentPreset: 'standard' });
  assert.equal(team.ensureRedteamTeamMode(switched), 'skip-not-redteam');
  switched.events.push({ type: 'agent-preset/selected', data: { agentPreset: 'redteam' } });
  assert.equal(team.ensureRedteamTeamMode(switched), 'enabled');
});

check('重试：默认 3、续跑关闭、鉴权与用户取消不重复执行', () => {
  assert.equal(retry.DEFAULT_CONTINUE_RETRY.retryMax, 3);
  assert.equal(retry.DEFAULT_CONTINUE_RETRY.autoContinue, false);
  assert.equal(retry.shouldAutoRetry({ code: 'AUTH' }), false);
  assert.equal(retry.shouldAutoRetry({ code: 'TRANSPORT' }), true);
  assert.equal(retry.shouldAutoRetry({ code: 'TRANSPORT' }, { aborted: true }), false);
  assert.equal(retry.shouldAutoContinue({ kind: 'aborted', reason: 'user' }), false);
});

console.log(JSON.stringify({ checks, patches: core.ALL_PATCHES.map((p) => ({ id: p.id, name: p.name })) }));
