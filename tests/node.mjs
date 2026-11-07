import assert from 'node:assert/strict';
import {createLangChainTool} from '../packages/npm/index.js';
const expected = {ok:true,tier:'delayed',delay_sec:7200,age_sec:7300,walls:[],truth:{unmeasured:true}};
const seen = [];
const tool = await createLangChainTool({fetch: async(url, init) => {
  seen.push({url,init}); return {ok:true,status:200,json:async()=>expected};
}});
assert.deepEqual(await tool.invoke({symbol:'BTCUSDT'}), expected);
assert.equal(seen.length, 1);
assert.equal(seen[0].init.headers.Authorization, undefined);
console.log('LangChain Node adapter: fixture data preserved, one call, no key');
