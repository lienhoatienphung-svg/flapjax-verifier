#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Unit and live BSC Mainnet verification test suite for flapjax_verifier.py."""

import hashlib
import unittest
import flapjax_verifier as fv


class TestFlapJaxVerifier(unittest.TestCase):
    def test_01_constants_and_addresses(self):
        self.assertEqual(len(fv.FLAPJAX_TOKEN), 42)
        self.assertEqual(len(fv.TREASURY), 42)
        self.assertEqual(len(fv.ARISPAY_SETTLED_RECEIPTS), 7)
        self.assertEqual(sum(r["amount_fj"] for r in fv.ARISPAY_SETTLED_RECEIPTS), 1900000)

    def test_02_all_buyback_hashes_are_valid_64_hex(self):
        self.assertEqual(len(fv.VERIFIED_BUYBACKS), 8)
        for b in fv.VERIFIED_BUYBACKS:
            tx = b["tx"]
            self.assertTrue(tx.startswith("0x") and len(tx) == 66)
            int(tx[2:], 16)

    def test_03_all_arispay_receipt_hashes_are_valid_64_hex(self):
        for r in fv.ARISPAY_SETTLED_RECEIPTS:
            tx = r["tx"]
            self.assertTrue(tx.startswith("0x") and len(tx) == 66)
            int(tx[2:], 16)

    def test_04_two_percent_depth_formula_and_sqrt_ratio(self):
        liq = 320678316678999036604866
        sqrt_p = 5249004968937877293685143
        depth = fv.compute_two_percent_wbnb_depth(liq, sqrt_p)
        self.assertAlmostEqual(depth, 0.06564, places=4)

    def test_05_live_flapjax_bytecode_and_renounced_storage(self):
        code = fv.rpc_call("eth_getCode", [fv.FLAPJAX_TOKEN, "latest"])
        raw = bytes.fromhex(code[2:])
        self.assertEqual(len(raw), 2901)
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            "44f1b21bd296f3dcc03154e55a619a4e217d12abb02eef8ad7413696176b4cfd",
        )
        owner_slot = fv.rpc_call("eth_getStorageAt", [fv.FLAPJAX_TOKEN, "0x5", "latest"])
        mode_slot = fv.rpc_call("eth_getStorageAt", [fv.FLAPJAX_TOKEN, "0x6", "latest"])
        self.assertEqual(int(owner_slot, 16), 0)
        self.assertEqual(int(mode_slot, 16), 0)

    def test_06_live_goplus_locker_locks_101(self):
        data = "0xf4dadc61" + hex(101)[2:].rjust(64, "0")
        res = fv.rpc_call("eth_call", [{"to": fv.GOPLUS_LOCKER, "data": data}, "latest"])
        clean = res[2:]
        nft_id = int(clean[64:128], 16)
        end_time = int(clean[320:384], 16)
        self.assertEqual(nft_id, 1456181)
        self.assertEqual(end_time, 2048764401)

    def test_07_live_erc8004_dispatcher_31_selectors(self):
        code = fv.rpc_call("eth_getCode", [fv.ERC8004_IMPL, "latest"])
        raw = bytes.fromhex(code[2:])
        self.assertEqual(len(raw), 14474)
        sels = fv.extract_dispatcher_push4(code)
        self.assertEqual(len(sels), 31)
        self.assertEqual(sels[0]["offset"], "0x29")
        self.assertEqual(sels[0]["selector"], "0x01ffc9a7")
        self.assertEqual(sels[-1]["offset"], "0x172")
        self.assertEqual(sels[-1]["selector"], "0xf2fde38b")

    def test_08_live_secondary_btcb_pool_state(self):
        btcb_wei = fv.erc20_balance_of(fv.BTCB_TOKEN, fv.POOL_V3_BTCB)
        fj_wei = fv.erc20_balance_of(fv.FLAPJAX_TOKEN, fv.POOL_V3_BTCB)
        self.assertEqual(btcb_wei, 183970635465278)
        self.assertEqual(fj_wei, 5619844348598993998769163970)

    def test_09_live_verify_all_7_arispay_receipts_and_retention(self):
        for item in fv.ARISPAY_SETTLED_RECEIPTS:
            chk = fv.verify_transfer_receipt(item["tx"], fv.ARISPAY_WALLET, item["amount_fj"] * (10**18))
            self.assertTrue(chk["valid"], f"Receipt failed: {item['bounty']}")
            self.assertEqual(chk["blockNumber"], item["block"])
        live_bal = fv.erc20_balance_of(fv.FLAPJAX_TOKEN, fv.ARISPAY_WALLET)
        self.assertGreaterEqual(live_bal, 1900000 * (10**18))

    def test_10_plus_one_wei_tamper_rejection(self):
        first = fv.ARISPAY_SETTLED_RECEIPTS[0]
        tampered = fv.verify_transfer_receipt(first["tx"], fv.ARISPAY_WALLET, first["amount_fj"] * (10**18) + 1)
        self.assertFalse(tampered["valid"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
