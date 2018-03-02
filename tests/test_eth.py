import struct
import unittest
import os

from manticore.ethereum import ManticoreEVM, IntegerOverflow
from manticore.ethereum import ABI

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

# FIXME(mark): Remove these two lines when logging works for ManticoreEVM
from manticore.utils.log import init_logging
init_logging()

class EthDetectors(unittest.TestCase):
    def test_int_ovf(self):
        mevm = ManticoreEVM()
        mevm.register_detector(IntegerOverflow())
        filename = os.path.join(THIS_DIR, 'binaries/int_overflow.sol')
        mevm.multi_tx_analysis(filename)
        self.assertEqual(len(mevm.global_findings), 3)
        all_findings = ''.join(map(lambda x: x[2], mevm.global_findings))
        self.assertIn('underflow at SUB', all_findings)
        self.assertIn('overflow at ADD', all_findings)
        self.assertIn('overflow at MUL', all_findings)

class EthereumAbiTests(unittest.TestCase):
    @staticmethod
    def _pack_int_to_32(x):
        return '\x00' * 28 + struct.pack('>I', x)

    def test_dyn_address(self):
        d = [
            'AAAA',                    # function hash
            self._pack_int_to_32(32),  # offset to data start
            self._pack_int_to_32(2),   # data start; # of elements
            self._pack_int_to_32(42),  # element 1
            self._pack_int_to_32(43),  # element 2
        ]
        d = ''.join(d)

        funcname, dynargs = ABI.parse(type_spec='func(address[])', data=d)

        self.assertEqual(funcname, 'func')
        self.assertEqual(dynargs, ([42, 43],))
