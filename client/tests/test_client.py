import unittest
import test.support
from client import bkup
import os
import pathlib
import tempfile
import time
import subprocess


class TestFoo(unittest.TestCase):

    def setUp(self) -> None:
        self.failed = False

    # dump stdout/err if command failed
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

    # create file tree for test
    def create_test_tree(self, dir: pathlib.Path, depth: int, dir_count: int, file_count: int) -> int:
        count = 0
        if depth > 0:
            for i in range(dir_count):
                cdir = dir / f"dir{i}"
                cdir.mkdir()
                count += self.create_test_tree(cdir, depth - 1, dir_count, file_count)

        for i in range(file_count):
            content = f"file{i}"
            cfile = dir / content
            with cfile.open("w") as fout:
                fout.write(content)
            count += 1

        return count

    # check if directory trees have the same structure
    def check_tree(self, dir1: pathlib.Path, dir2: pathlib.Path):
        subfile1 = [p.name for p in dir1.iterdir() if p.is_file()]
        subfile1.sort()
        subfile2 = [p.name for p in dir2.iterdir() if p.is_file()]
        subfile2.sort()
        self.assertEqual(subfile1, subfile2)

        subdir1 = [p.name for p in dir1.iterdir() if p.is_dir()]
        subdir1.sort()
        subdir2 = [p.name for p in dir2.iterdir() if p.is_dir()]
        subdir2.sort()
        self.assertEqual(subdir1, subdir2)

        for name in subdir1:
            self.check_tree(dir1 / name, dir2 / name)

    def extract_archive(self, archive_file: pathlib.Path, dst_dir: pathlib.Path):
        exts = archive_file.suffixes
        if exts[0] == ".tar":
            subprocess.run(["tar", "-C", str(dst_dir), "-xf", str(archive_file)], check=True)
        elif exts == [".7z"]:
            prog = os.path.expandvars("%ProgramFiles%\\7-Zip\\7z.exe")
            print([prog, "x", f"-o{str(dst_dir)}", str(archive_file)])
            subprocess.run([prog, "x", f"-o{str(dst_dir)}", str(archive_file)], check=True)
        else:
            self.fail(f"Unknown archive type: {archive_file.name}")

    def test_help(self):
        stdout, stderr = self.call_main(["bkup.py", "-h"])
        self.assertTrue(stdout or stderr)

    def test_sync(self):
        with tempfile.TemporaryDirectory() as src, tempfile.TemporaryDirectory() as dst:
            srcdir = pathlib.Path(src)
            dstdir = pathlib.Path(dst)
            # "src/"
            if not src.endswith(os.path.sep):
                src += os.path.sep
            # create a tree to src
            self.create_test_tree(srcdir, depth=2, dir_count=10, file_count=50)
            # create a different tree to dst
            self.create_test_tree(dstdir, depth=1, dir_count=5, file_count=100)
            # sync src > dst
            self.call_main(["bkup.py", "sync", "--src", src, "--dst", dst, "--force"])
            # check src == dst
            self.check_tree(srcdir, dstdir)

    def test_clean(self):
        now = time.time()
        day = 24.0 * 60 * 60
        with tempfile.TemporaryDirectory() as tmpdir:
            dir = pathlib.Path(tmpdir)
            for i in range(100):
                p = dir / f"backup_2024{i:0>4}.tar.bz2"
                p.touch()
                # (i + 0.5) days before
                ts = now - (i + 0.5) * day
                os.utime(p, (ts, ts))

            self.call_main(["bkup.py", "clean", "--dst", tmpdir, "--keep-count", "10", "--keep-days", "50"])

            result = list(dir.iterdir())
            self.assertEqual(len(result), 50)

            self.call_main(["bkup.py", "clean", "--dst", tmpdir, "--keep-count", "10", "--keep-days", "0"])

            result = list(dir.iterdir())
            self.assertEqual(len(result), 10)

    def test_archive(self):
        # python 3.9 dependent
        with (tempfile.TemporaryDirectory() as src,
                tempfile.TemporaryDirectory() as dst,
                tempfile.TemporaryDirectory() as ext):
            srcdir = pathlib.Path(src)
            dstdir = pathlib.Path(dst)
            extdir = pathlib.Path(ext)

            self.create_test_tree(srcdir, depth=2, dir_count=10, file_count=50)

            # eusure dst dir is empry
            before = [p.name for p in dstdir.iterdir()]
            self.assertEqual(before, [])

            self.call_main(["bkup.py", "archive", "--src", src, "--dst", dst])

            # eusure dst dir has an archive file and latest.txt
            after = [p.name for p in dstdir.iterdir() if p.name != "latest.txt"]
            self.assertEqual(len(after), 1)
            archive_file = dstdir / after[0]
            latest_file = dstdir / "latest.txt"

            # check latest.txt
            with latest_file.open("r") as fin:
                line = fin.readline().strip()
                line == after[0]

            # extract and check the archive file
            self.extract_archive(archive_file, extdir)

            # if there is only one dir, change extdir to it
            subs = list(extdir.iterdir())
            if len(subs) == 1:
                extdir = subs[0]
            self.check_tree(srcdir, extdir)


if __name__ == '__main__':
    unittest.main()
