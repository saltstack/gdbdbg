#!/bin/sh
#
# Build a ppt wheel in a docker container.
#
# This script is meant to build a wheel in the same docker container images as
# we do in CI/CD. Run it from the root of the github repository.
#
#  `scripts/dockerbuild.sh1
#
if [ -n "$UID" ]
then
  CHOWN=""
else
  CHOWN="" #chown -R $UID dist build src/ppbt/_toolchain"
fi

export CHOWN

CMD="
apt-get update;
apt-get install -y gcc python3 \
   python3-pip python3-venv build-essential patchelf m4 texinfo
cd /src
python3 -m venv venv
venv/bin/pip install build wheel setuptools
venv/bin/python3 -m build
$CHOWN
"

docker run --rm -v $(pwd):/src debian:11 /bin/sh -c "$CMD"
