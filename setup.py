# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
import platform

from setuptools import Distribution, setup

GLIBC_VERSION = "2.17"


def plat_name():
    return f"manylinux_{GLIBC_VERSION.replace('.', '_')}_{platform.machine()}"


options = {
    "bdist_wheel": {
        "python_tag": "py3",
    }
}

if platform.system() == "Linux":
    options["bdist_wheel"]["plat_name"] = plat_name()


setup(options=options)
