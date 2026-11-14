#!/bin/bash

set -ex

PATH_DEB=$(realpath -e "$1")

PATH_OUT="$2"

mkdir -vp "$PATH_OUT"

PATH_OUT_OK=$(realpath -e "$PATH_OUT")

cd "$PATH_OUT_OK"

PATH_PKG="$PATH_OUT_OK"/"package.deb"

cp -v "$PATH_DEB" "$PATH_PKG"

ar -x "$PATH_PKG"

tar -xvf "data.tar.xz"
