import pathlib
import subprocess
import sys

real_gdb_bin = pathlib.Path(__file__) / "gdb", "bin", "gdb"

def main():
    if hasattr(sys, "RELENV"):
        os.environ["PYTHON_HOME"] = f"{sys.RELENV}"
        subprocess.popen([str(real_gdb_bin)])
    else:
        sys.stderr.write(
            "Not running in a relenv environment."
        )
        sys.stderr.flush()
        sys.exit(1)
