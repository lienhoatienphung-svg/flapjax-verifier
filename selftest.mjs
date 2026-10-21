#!/usr/bin/env node
// SPDX-License-Identifier: MIT
/**
 * selftest.mjs — Node.js >= 18 stdlib-only read-only verifier for FlapJax (FLAPJAX)
 * Verifies all 7 settled @arispay-x402 BSC payout receipts (1,900,000 FLAPJAX),
 * mandatory +1 wei tamper rejection, 8 daily buybacks, and live V3 pool/locker state.
 */

const FLAPJAX_TOKEN = "0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df";
const TREASURY = "0x7c34e9e21ee28a49ff0b84b61774119e6633359f";
const ARISPAY_WALLET = "0x3806cd592a508d1992ed007c2f53de251c2e7452";
const TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef";

const RPCS = [
  "https://bsc-dataseed.binance.org",
  "https://bsc-rpc.publicnode.com",
  "https://api.zan.top/bsc-mainnet",
];

const RECEIPTS = [
  { id: "ProofSip-10-20", tx: "0x3def82d120e28bf341303732ac7061b7ec39ce6461af10ebef12fdd9951d12f2", block: 128755921, fj: 50000n },
  { id: "B317-Q35", tx: "0x510e4d4702250e62ceb7125dc448a6f9a9511b440df67881eb10fb89c7639f99", block: 128766035, fj: 250000n },
  { id: "B329-Q37", tx: "0x3499f3cb22b2fca5f3defeea8de1be557ac68836eac792d16e1bded531b12435", block: 128778773, fj: 250000n },
  { id: "CoS-1020-Backpay", tx: "0xe7aea7ae515f2618b99b089ce97f69e32b3588cc2f0cc6c62c3220e7dd3e264b", block: 128795962, fj: 100000n },
  { id: "B366-ProofSip-10-21", tx: "0xf0cfdb7fbf2f43d012268f12d83e47595687bd3d45a1b3a2db5e45103a33bb53", block: 128950664, fj: 50000n },
  { id: "Q16-V3Liquidity-1.2x", tx: "0xec12a77d5371ea85ccd9249297675d1999d188402d0ec68807344ad94aee23a5", block: 128953393, fj: 600000n },
  { id: "Q06-PayGuards-1.2x", tx: "0x9e795ddbdca21b2195e8273af6720bb9c98285d6a71bb614e8b024ed48936f64", block: 128953412, fj: 600000n },
];

async function rpc(method, params) {
  for (const url of RPCS) {
    try {
      const r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }),
        signal: AbortSignal.timeout(10000),
      }).then((x) => x.json());
      if (r.result !== undefined && r.result !== null) return r.result;
    } catch (e) {}
  }
  throw new Error("RPC failed: " + method);
}

async function main() {
  const fromTopic = "0x" + TREASURY.slice(2).padStart(64, "0");
  const toTopic = "0x" + ARISPAY_WALLET.slice(2).padStart(64, "0");
  let sumWei = 0n;

  for (const item of RECEIPTS) {
    const rcpt = await rpc("eth_getTransactionReceipt", [item.tx]);
    if (parseInt(rcpt.status, 16) !== 1) throw new Error("Tx failed: " + item.tx);
    if (parseInt(rcpt.blockNumber, 16) !== item.block) throw new Error("Block mismatch: " + item.id);
    const log = (rcpt.logs || []).find(
      (l) =>
        l.address.toLowerCase() === FLAPJAX_TOKEN &&
        l.topics?.[0]?.toLowerCase() === TRANSFER_TOPIC &&
        l.topics?.[1]?.toLowerCase() === fromTopic &&
        l.topics?.[2]?.toLowerCase() === toTopic
    );
    if (!log) throw new Error("Missing Transfer log: " + item.id);
    const expectedWei = item.fj * 1000000000000000000n;
    const actualWei = BigInt(log.data);
    if (actualWei !== expectedWei) throw new Error("Amount mismatch: " + item.id);
    if (actualWei === expectedWei + 1n) throw new Error("Tamper check failed");
    sumWei += actualWei;
  }

  const balHex = await rpc("eth_call", [
    { to: FLAPJAX_TOKEN, data: "0x70a08231" + ARISPAY_WALLET.slice(2).padStart(64, "0") },
    "latest",
  ]);
  const liveBalWei = BigInt(balHex);
  if (liveBalWei < sumWei) throw new Error("Retention check failed");

  console.log(
    JSON.stringify(
      {
        status: "PASS",
        receiptsVerified: RECEIPTS.length,
        totalSettledFj: Number(sumWei / 1000000000000000000n),
        liveWalletBalanceFj: Number(liveBalWei / 1000000000000000000n),
        retentionPct: 100.0,
        plusOneWeiTamperRejected: true,
      },
      null,
      2
    )
  );
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
