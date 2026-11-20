// Exercise a real installed package tree with a single, explicit target.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const [rootArg,packageName,operation]=process.argv.slice(2);
const root=fs.realpathSync(rootArg);
assert(root.includes(path.join('build','tmp','live-acceptance')),'Disposable workspace required');
const aiBase=path.join(root,'node_modules','@deepseek-ai');
const core=await import(pathToFileURL(path.join(root,'node_modules',packageName,'lib/core.js')).href);
const inside=p=>{const r=path.relative(root,path.resolve(p));return r!== '..'&&!r.startsWith('..'+path.sep)&&!path.isAbsolute(r);};
const flatten=value=>Array.isArray(value)?value.flatMap(flatten):value&&typeof value==='object'?Object.values(value).flatMap(flatten):typeof value==='string'&&value?[value]:[];
const targets=[...new Set(flatten(core.targetFiles(aiBase)))];
assert(targets.every(inside),'Refuse target outside disposable tree: '+targets.filter(p=>!inside(p)));
let result;
if(operation==='apply') result=await core.applyPatches(aiBase,core.ALL_PATCHES,{preserveClientBundles:false});
else if(operation==='revert') result=await core.revertAll(aiBase);
else if(operation==='status') result=await core.patchStatus(aiBase);
else if(operation==='targets') result=targets;
else throw new Error('Unknown operation');
console.log(JSON.stringify({package:packageName,operation,aiBase,result}));
