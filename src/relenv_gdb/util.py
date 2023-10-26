# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Utility methods.
"""
import pathlib


def find_dist_info():
    """Find relenv_gdb's dist-info directory."""
    for name in pathlib.Path(__file__).parent.parent.rglob("relenv_gdb*dist-info"):
        return name


def find_relenv_gdb():
    """Find the relenv-gdb script location."""
    dist_info = find_dist_info()
    text = pathlib.Path(dist_info, "RECORD").read_text()
    for line in text.split("\n"):
        if "bin/relenv-gdb" in line:
            location, digest, size = line.rsplit(",", 2)
            script = (pathlib.Path(dist_info).parent / location).resolve()
            if script.exists():
                return script


def append_line(path, line):
    """
    Append a line to the path.
    """
    if isinstance(path, (str, pathlib.Path)):
        with open(path, "a") as fp:
            fp.write(line + "\n")
    else:
        path.write(line + "\n")
        path.flush()
