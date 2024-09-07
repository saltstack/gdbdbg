# Copyright 2023-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
"""
Localize gdb startup to the current relenv.
"""
import os
import pathlib
import sys

real_gdb_bin = pathlib.Path(__file__).parent / "gdb" / "bin" / "gdb"
data_directory = pathlib.Path(__file__).parent / "gdb" / "share" / "gdb"


def main():
    """Wrap gdb startup."""
    os.environ["PYTHONPATH"] = os.pathsep.join(sys.path)
    if os.execve in os.supports_fd:
        with open(real_gdb_bin, "rb") as fp:
            sys.stdout.flush()
            sys.stderr.flush()
            args = [sys.argv[0], f"--data-directory={data_directory}"] + sys.argv[1:]
            os.execve(fp.fileno(), args, os.environ)
    else:
        cmd = real_gdb_bin
        args = [real_gdb_bin, f"--data-directory={data_directory}"] + sys.argv[1:]
        os.execve(cmd, args, os.environ)
