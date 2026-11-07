const description = 'Read liquidation walls, snapshot age, evidence labels and the public record. Free data is 2 hours behind on six coins. Descriptive data, not trading advice.';

export class HunterKillerError extends Error {
  constructor(status, body) { super(`Hunter Killer HTTP ${status}`); this.status = status; this.body = body; }
}

export async function getLevels(symbol, {key, probe = false, fetch: fetcher = globalThis.fetch} = {}) {
  symbol = String(symbol).trim().toUpperCase();
  if (!/^[A-Z0-9]{2,20}$/.test(symbol)) throw new TypeError('Use a pair such as BTCUSDT');
  const headers = {Accept: 'application/json', 'User-Agent': 'hunterkiller-agent-tools/0.1.0'};
  if (key) headers.Authorization = `Bearer ${key}`;
  if (probe) headers['X-HK-Probe'] = '1';
  const res = await fetcher(`https://hunterkiller.io/api/v1/levels/${symbol}`, {
    headers, signal: AbortSignal.timeout(15000), redirect: 'error'
  });
  const body = await res.json().catch(() => ({error: 'non_json_response'}));
  if (!res.ok || !body || body.ok !== true) throw new HunterKillerError(res.status, body);
  return body;
}

export async function createLangChainTool(options = {}) {
  const [{tool}, {z}] = await Promise.all([import('@langchain/core/tools'), import('zod')]);
  return tool(({symbol}) => getLevels(symbol, options), {
    name: 'hunterkiller_levels', description,
    schema: z.object({symbol: z.string().describe('Pair such as BTCUSDT')})
  });
}

// Responses API function definition. Dispatch only this named read-only function.
export const openAIFunction = {
  type: 'function', name: 'hunterkiller_levels', description, strict: true,
  parameters: {type: 'object', properties: {symbol: {type: 'string', description: 'Pair such as BTCUSDT'}}, required: ['symbol'], additionalProperties: false}
};

// A definition for application bindings, not a claim of hosted catalog inclusion.
export const composioToolDefinition = {
  slug: 'HUNTERKILLER_LEVELS', name: 'Hunter Killer levels', description,
  inputParameters: openAIFunction.parameters
};
