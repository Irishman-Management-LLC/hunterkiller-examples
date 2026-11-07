# Hunter Killer agent tools

```sh
npm install hunterkiller-agent-tools@0.1.0
```

```js
import {getLevels} from 'hunterkiller-agent-tools';
console.log(await getLevels('BTCUSDT'));
```

With LangChain, also install `@langchain/core` and `zod`, then
`const tool = await createLangChainTool(); await tool.invoke({symbol: 'BTCUSDT'})`.
The package exports `openAIFunction` for Responses function calling and
`composioToolDefinition` for custom application bindings. CrewAI is a Python
framework; use the separate `hunterkiller-crewai` package.

Free data is 2 hours behind on six coins. Source JSON, evidence labels, snapshot
age and record links stay intact. Keys are optional application configuration
in `getLevels(symbol, {key})`; no environment credentials are read automatically.
Calls have a 15 second timeout, no automatic retry and no payment behavior.
An HTTP failure rejects the promise. No fabricated ladder replaces a failure.
The package and keyless endpoint must be released before this example works.
