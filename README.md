# flapjax-verifier

Zero-dependency, 100% read-only BNB Smart Chain verification CLI and 11-test suite for **FlapJax (`FLAPJAX`, `0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df`)**, built by **`@arispay-x402`** (wallet `0x3806cd592a508d1992Ed007C2F53de251C2E7452`).

## Features
- **100% Read-Only & Stdlib Only**: Uses only standard library JSON-RPC calls (`eth_call`, `eth_getStorageAt`, `eth_getCode`, `eth_getBalance`, `eth_getTransactionReceipt`, `eth_blockNumber`). Zero private keys, zero external packages.
- **Accepts Any Wallet or Arbitrary Transaction List**:
  - Pass `--wallet 0xYourWallet` and/or `--txs 0xTx1,0xTx2,...` (or `--txs-file path.json`) to `flapjax_verifier.py receipts` or `node selftest.mjs` to verify any agent wallet, any treasury payout list, or any buyback transaction on BSC.
- **What the 11-Test Suite Verifies**:
  1. `FLAPJAX` runtime bytecode (`2,901 bytes`, SHA-256 `44f1b21bd296f3dcc03154e55a619a4e217d12abb02eef8ad7413696176b4cfd`) and renounced storage (`slot[5] _owner == 0x0`, `slot[6] _mode == 0`).
  2. GoPlus `UniV3LPLocker` (`0x25c9c4b56e820e0dea438b145284f02d9ca9bd52`) `locks(101)` (`word[7] nftId = 1456181`, `word[9] endTime = 2048764401` / `2034-12-03T13:13:21Z`).
  3. Primary PancakeSwap V3 `FLAPJAX/WBNB` 1% pool (`0xcA93EC685b8623688E6B236f9068034B298c2150`) exact closed-form `+2%` WBNB depth (`0.06564 WBNB` at `L = 320678316678999036604866`, `sqrtPriceX96 = 1627163852510051447001980`) and Secondary `BTCB/FLAPJAX` V3 pool (`0x740a3b4a91cb8fa47e85d7f9713ca6ec2f8a037e`) reserves.
  4. ERC-8004 Identity Registry (`0x7274e874ca62410a93bd8bf61c69d8045e399c02`) 31-selector linear bytecode dispatcher walk (`0x29..0x172`).
  5. Arbitrary wallet & custom transaction list verification (`test_11_arbitrary_wallet_and_custom_tx_list`), all **7 settled `@arispay-x402` on-chain BSC payout receipts (`1,900,000 FLAPJAX`)**, `100.0%` holder retention check, and mandatory `+1 wei` tamper-rejection test.

## Quickstart

```bash
git clone https://github.com/lienhoatienphung-svg/flapjax-verifier.git
cd flapjax-verifier
python3 -m unittest -v
python3 flapjax_verifier.py state
python3 flapjax_verifier.py receipts
python3 flapjax_verifier.py receipts --wallet 0x7c34e9e21ee28a49ff0b84b61774119e6633359f --txs 0xe9ea4a165aae8eb4228ef073a93c4c1983894104a426e9f5d64b0214cfde3369
node selftest.mjs
```

## License
MIT License (see `LICENSE`).
