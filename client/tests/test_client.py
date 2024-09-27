import unittest
import test.support
from client import bkup


class TestFoo(unittest.TestCase):

    # dump stdout/err if failed
    def tearDown(self):
        if self.failed:
            if self.stdout:
                print()
                print("=== stdout " + "=" * 69)
                print(self.stdout)
                print("=== end of stdout " + "=" * 62)
            if self.stderr:
                print()
                print("=== stderr " + "=" * 69)
                print(self.stderr)
                print("=== end of stderr " + "=" * 62)

    # call bkup.main with stdio redirect and sys.exit() handling
    def call_main(self, argv: list[str]):
        with test.support.captured_stdout() as stdout, test.support.captured_stderr() as stderr:
            try:
                bkup.main(argv)
                self.failed = False
            except SystemExit as e:
                self.failed = bool(e.code)
                self.assertFalse(e.code, "bkup.main failed")
            except Exception:
                self.failed = True
                raise
            finally:
                self.stdout = stdout.getvalue()
                self.stderr = stderr.getvalue()

        return stdout.getvalue(), stderr.getvalue()

    def test_help(self):
        stdout, stderr = self.call_main(["bkup.py", "-h"])
        self.assertTrue(stdout or stderr)

    def test_sync(self):
        self.call_main(["bkup.py", "sync", "-h"])


if __name__ == '__main__':
    unittest.main()
