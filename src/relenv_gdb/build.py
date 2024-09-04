# Copyright 2023-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
"""
Build our python wheel.
"""
import contextlib
import logging
import os
import pathlib
import pprint
import shutil
import subprocess
import sys

import relenv.build
import relenv.buildenv
import relenv.common
import relenv.create
import relenv.fetch
import relenv.toolchain
from setuptools.build_meta import *

_build_wheel = build_wheel


@contextlib.contextmanager
def pushd(path):
    """
    A pushd context manager.
    """
    orig = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(orig)


def build_gdb(prefix):
    """Compile and install gdb to the prefix."""
    src = prefix / "src"
    src.mkdir(exist_ok=True)

    os.environ.update(relenv.buildenv.buildenv(prefix))
    os.environ["CFLAGS"] = (
        f"{os.environ['CFLAGS']} -I{os.environ['RELENV_PATH']}/include/ncursesw "
        f"-I{os.environ['RELENV_PATH']}/include/readline "
        f"-I{os.environ['RELENV_PATH']}/lib/python3.10/site-packages/relenv_gdb/gdb/include"
    )
    os.environ["CPPFLAGS"] = (
        f"{os.environ['CPPFLAGS']} -I{os.environ['RELENV_PATH']}/include/ncursesw "
        f"-I{os.environ['RELENV_PATH']}/include/readline "
        f"-I{os.environ['RELENV_PATH']}/lib/python3.10/site-packages/relenv_gdb/gdb/include"
    )
    os.environ["LDFLAGS"] = (
        f"{os.environ['LDFLAGS']} "
        f"-L{os.environ['RELENV_PATH']}/lib/python3.10/site-packages/relenv_gdb/gdb/lib "
    )

    print(f"Build environment: {pprint.pformat(dict(os.environ))}")
    sys.stdout.flush()

    url = "https://gmplib.org/download/gmp/gmp-6.3.0.tar.xz"
    relenv.common.download_url(
        url,
        src,
    )
    archive_name = str(src / pathlib.Path(url).name)
    relenv.common.extract_archive(str(src), archive_name)
    dir_name = archive_name.split(".tar")[0]

    with pushd(src / dir_name):
        subprocess.run(
            [
                "./configure",
                f"--prefix={os.environ['RELENV_PATH']}/lib/python3.10/site-packages/relenv_gdb/gdb",
            ],
            check=True,
        )
        subprocess.run(["make"], check=True)
        subprocess.run(["make", "install"], check=True)

    url = "https://www.mpfr.org/mpfr-current/mpfr-4.2.1.tar.xz"
    relenv.common.download_url(
        url,
        src,
    )
    archive_name = str(src / pathlib.Path(url).name)
    relenv.common.extract_archive(str(src), archive_name)
    dir_name = archive_name.split(".tar")[0]

    with pushd(src / dir_name):
        subprocess.run(
            [
                "./configure",
                f"--prefix={os.environ['RELENV_PATH']}/lib/python3.10/site-packages/relenv_gdb/gdb",
            ],
            check=True,
        )
        subprocess.run(["make"], check=True)
        subprocess.run(["make", "install"], check=True)

    os.environ["LDFLAGS"] = f"{os.environ['LDFLAGS']} -lreadline"
    url = "https://ftp.gnu.org/gnu/gdb/gdb-15.1.tar.xz"
    relenv.common.download_url(
        url,
        src,
    )
    archive_name = str(src / pathlib.Path(url).name)
    relenv.common.extract_archive(str(src), archive_name)
    dir_name = archive_name.split(".tar")[0]
    with pushd(src / dir_name):
        subprocess.run(
            [
                "./configure",
                f"--prefix={os.environ['RELENV_PATH']}/lib/python3.10/site-packages/relenv_gdb/gdb",
                f"--with-python={os.environ['RELENV_PATH']}/bin/python3",
                "--with-lzma",
                "--with-separate-debug-dir=/usr/lib/debug",
            ],
            check=True,
        )
        subprocess.run(["make"], check=True)
        bins = ["gdb/gdb", "gdbserver/gdbserver", "gdbserver/libinproctrace.so"]
        for _ in bins:
            if not pathlib.Path(_).resolve().exists():
                print(f"File not found {_}")
            subprocess.run(
                [
                    "patchelf",
                    "--add-rpath",
                    f"{os.environ['TOOLCHAIN_PATH']}/{os.environ['TRIPLET']}/sysroot/lib",
                    _,
                ],
                check=True,
            )
        subprocess.run(["make", "install"])

    relenv.relocate.main(
        f"{os.environ['RELENV_PATH']}/lib/python3.10/site-packages/relenv_gdb/gdb",
        f"{os.environ['RELENV_PATH']}/lib/python3.10/site-packages/relenv_gdb/gdb/lib",
        False,
    )
    shutil.copytree(
        f"{os.environ['RELENV_PATH']}/lib/python3.10/site-packages/relenv_gdb/gdb",
        "src/relenv_gdb/gdb",
    )


def build_wheel(wheel_directory, metadata_directory=None, config_settings=None):
    """PEP 517 wheel creation hook."""
    logging.basicConfig(level=logging.DEBUG)

    dirs = relenv.common.work_dirs()
    if not dirs.toolchain.exists():
        os.makedirs(dirs.toolchain)
    if not dirs.build.exists():
        os.makedirs(dirs.build)

    arch = relenv.common.build_arch()
    triplet = relenv.common.get_triplet(machine=arch)

    python = relenv.build.platform_versions()[0]
    version = relenv.common.__version__

    root = pathlib.Path(os.environ.get("PWD", os.getcwd()))
    build = root / "build"

    relenvdir = (build / "gdb").resolve()

    relenv.toolchain.fetch(arch, dirs.toolchain)
    relenv.fetch.fetch(version, triplet, python)
    if not relenvdir.exists():
        relenv.create.create(str(relenvdir), version=python)
    build_gdb(relenvdir)
    return _build_wheel(wheel_directory, metadata_directory, config_settings)
