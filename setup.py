# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
import platform

from setuptools import Distribution, setup


GLIBC_VERSION = "2.17"


def plat_name():
    return f"manylinux_{GLIBC_VERSION.replace('.', '_')}_{platform.machine()}"

setup(
    options={
        "bdist_wheel": {
            "plat_name": f"{plat_name()}",
            "python_tag": "py3",
        }
    }
)
