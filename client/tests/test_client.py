import unittest
import test.support
from client import bkup


class TestFoo(unittest.TestCase):

    def test_help(self):
        with test.support.captured_stdout() as stdout, test.support.captured_stderr() as stderr:
            with self.assertRaises(SystemExit) as ctx:
                bkup.main(["bkup.py", "-h"])
        e: SystemExit = ctx.exception
        self.assertEqual(e.code, 0)
        self.assertTrue(stdout.getvalue() or stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
