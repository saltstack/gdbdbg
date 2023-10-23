import contextlib
import pathlib
import subprocess
import tempfile
import os
import shutil

from setuptools import build_meta as _orig
from setuptools.build_meta import *

import relenv.common
import relenv.create
import relenv.buildenv


_build_wheel = build_wheel


@contextlib.contextmanager
def pushd(path):
    orig = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(orig)


def build_gdb(prefix):

    src = prefix / "src"
    src.mkdir()

    url = "https://gmplib.org/download/gmp/gmp-6.3.0.tar.xz"
    relenv.common.download_url(
        url,
        src,
    )

    archive_name = str(src / pathlib.Path(url).name)
    relenv.common.extract_archive(str(src), archive_name)

    dir_name = archive_name.split(".tar")[0]
    os.environ.update(relenv.buildenv.buildenv(prefix))
    os.environ["CFLAGS"] = f"{os.environ['CFLAGS']} -I{os.environ['RELENV_PATH']}/include/ncursesw"
    os.environ["CPPFLAGS"] = f"{os.environ['CPPFLAGS']} -I{os.environ['RELENV_PATH']}/include/ncursesw"
    import pprint
    pprint.pprint(dict(os.environ))

    with pushd(src / dir_name):
        subprocess.run(["./configure", f"--prefix={os.environ['RELENV_PATH']}/lib/python3.10/site-packages/relenv_gdb/gdb"])
        subprocess.run(["make"])
        subprocess.run(["make", "install"])


    url = "https://ftp.gnu.org/gnu/gdb/gdb-13.2.tar.xz"
    relenv.common.download_url(
        url,
        src,
    )
    archive_name = str(src / pathlib.Path(url).name)
    relenv.common.extract_archive(str(src), archive_name)
    dir_name = archive_name.split(".tar")[0]
    #os.environ["LDFLAGS"] = f"{os.environ['LDFLAGS']} '-Wl,-rpath=$$ORIGIN/../lib'"
    with pushd(src / dir_name):
        subprocess.run([
            "./configure",
            f"--prefix={os.environ['RELENV_PATH']}/lib/python3.10/site-packages/relenv_gdb/gdb",
            f"--with-python={os.environ['RELENV_PATH']}/bin/python3",
            "--with-lzma",
        ])
        subprocess.run(["make"])
        subprocess.run(["patchelf", "--add-rpath", "$ORIGIN/../lib", "gdb/gdb"])
        subprocess.run(["make", "install"])
    relenv.relocate.main(os.environ["RELENV_PATH"])
    shutil.copytree(
        f"{os.environ['RELENV_PATH']}/lib/python3.10/site-packages/relenv_gdb/gdb",
        "src/relenv_gdb/gdb"
    )


def build_wheel(wheel_directory,
                metadata_directory=None, config_settings=None):
    """PEP 517 wheel creation hook"""
    static_build_dir = os.environ.get("PY_STATIC_BUILD_DIR", "")
    if static_build_dir:
        relenvdir = (pathlib.Path(static_build_dir) / "gdb").resolve()
        relenv.create.create(str(relenvdir))
        build_gdb(relenvdir)
        try:
            return _build_wheel(wheel_directory, metadata_directory, config_settings)
        finally:
            shutil.rmtree("src/relenv_gdb/gdb")
    else:
        with tempfile.TemporaryDirectory() as tmp_dist_dir:
            relenvdir = pathlib.Path(tmp_dist_dir) / "gdb"
            relenv.create.create(str(relenvdir))
            build_gdb(relenvdir)
            try:
                return _build_wheel(wheel_directory, metadata_directory, config_settings)
            finally:
                shutil.rmtree("src/relenv_gdb/gdb")
