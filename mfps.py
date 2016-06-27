#!/usr/bin/env python3
import sys
import os
import contextlib
import argparse
from subprocess import check_call, check_output
from tempfile import TemporaryDirectory
from pathlib import Path


def check_winnt(*, error=True):
    if not (sys.platform == "win32" and os.name == "nt"):
        if error:
            raise EnvironmentError("for compiler support windows NT only")

        return False

    return True

DEFAULT_MSDEV_PATH = Path(os.environ["SystemDrive"] + r"\MSDEV")
MSDEV_BIN = DEFAULT_MSDEV_PATH / "BIN"
FL32_EXE = MSDEV_BIN / "fl32.exe"


def add_env_path(name, path):
    # FPSVAR.bat behavior
    old = os.environ.get(name, "")
    new = str(path) + ";" + old

    os.environ[name] = new


def update_env():
    if getattr(update_env, "inited", False):
        return

    if FL32_EXE.exists():
        update_env.inited = True
        add_env_path("PATH", DEFAULT_MSDEV_PATH / "BIN")
        add_env_path("INCLUDE", DEFAULT_MSDEV_PATH / "INCLUDE")
        add_env_path("LIB", DEFAULT_MSDEV_PATH / "LIB")
    else:
        raise FileNotFoundError(str(FL32_EXE), "is missing")


@contextlib.contextmanager
def keep_chdir(target):
    current = os.getcwd()

    try:
        os.chdir(target)
        yield
    finally:
        os.chdir(current)


def compile_file(source, out=None):
    update_env()

    src_p = Path(source).absolute()
    out_p = src_p.parent / (src_p.stem + ".exe")

    if out:
        out_p = Path(out).absolute()

    with TemporaryDirectory() as temp, keep_chdir(temp):
        target_p = (Path(temp) / "TARGET.exe")

        # TODO: when call return != 0, raise another exception

        check_call([
            str(FL32_EXE),
            str(src_p),
            "/nologo",
            "/W0",
            "/link",
            "kernel32.lib",
            "/nologo",
            "/debug",
            "/subsystem:console",
            "/incremental:yes",
            "/machine:I386",
            '/out:TARGET.exe',
        ])

        content = target_p.read_bytes()
        out_p.write_bytes(content)


def main():
    # TODO: parse argument and redirect output
    parser = argparse.ArgumentParser()
    parser.add_argument("source", metavar="FILE")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    compile_file(args.source, args.out)


if __name__ == "__main__":
    main()
