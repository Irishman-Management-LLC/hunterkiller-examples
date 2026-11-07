// npm install hunterkiller-sdk; run with Node 20 or later.
import {deskRead} from 'hunterkiller-sdk';
console.log(JSON.stringify(await deskRead('BTCUSDT'), null, 2));
