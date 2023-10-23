import pathlib
import subprocess
import sys
import os

real_gdb_bin = pathlib.Path(__file__).parent / "gdb"/ "bin"/ "gdb"
data_directory = pathlib.Path(__file__).parent / "gdb"/ "share" /"gdb"

def main():
    if hasattr(sys, "RELENV"):
        os.environ["PYTHONHOME"] = f"{sys.RELENV}"
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
    else:
        sys.stderr.write(
            "Not running in a relenv environment."
        )
        sys.stderr.flush()
        sys.exit(1)
