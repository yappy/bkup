import unittest
import test.support
from client import bkup
import os
import pathlib
import tempfile


def create_test_tree(dir: pathlib.Path, depth: int, dir_count: int, file_count: int) -> int:
    count = 0
    if depth > 0:
        for i in range(dir_count):
            cdir = dir / f"dir{i}"
            cdir.mkdir()
            count += create_test_tree(cdir, depth - 1, dir_count, file_count)

    for i in range(file_count):
        content = f"file{i}"
        cfile = dir / content
        with cfile.open("w") as fout:
            fout.write(content)
        count += 1

    return count


class TestFoo(unittest.TestCase):

    def setUp(self) -> None:
        self.failed = False

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

    def check_tree(self, dir1: pathlib.Path, dir2: pathlib.Path):
        subdir1 = [p.name for p in dir1.iterdir() if p.is_dir()]
        subdir1.sort()
        subdir2 = [p.name for p in dir2.iterdir() if p.is_dir()]
        subdir2.sort()
        self.assertEqual(subdir1, subdir2)

        subfile1 = [p.name for p in dir1.iterdir() if p.is_file()]
        subfile1.sort()
        subfile2 = [p.name for p in dir2.iterdir() if p.is_file()]
        subfile2.sort()
        self.assertEqual(subfile1, subfile2)

    def test_help(self):
        stdout, stderr = self.call_main(["bkup.py", "-h"])
        self.assertTrue(stdout or stderr)

    def test_sync(self):
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as dst:
            srcdir = pathlib.Path(src)
            dstdir = pathlib.Path(dst)
            if not src.endswith(os.path.sep):
                src += os.path.sep
            # create a tree to src
            create_test_tree(srcdir, depth=2, dir_count=15, file_count=100)
            # create a different tree to dst
            create_test_tree(dstdir, depth=1, dir_count=5, file_count=200)
            # sync src > dst
            self.call_main(["bkup.py", "sync", "--src", src, "--dst", dst, "--force"])
            # check src == dst
            self.check_tree(srcdir, dstdir)


if __name__ == '__main__':
    unittest.main()
