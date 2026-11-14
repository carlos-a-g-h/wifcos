#!/bin/bash

set -e

SRC_FILE="sources.grub2-efi.txt"
PKG_DIR="dependency.grub2-efi"
TMPDIR="_tmp"

URL_FILE=$(awk '/^URL_FILE/ {print $NF}' "$SRC_FILE")
NAME_FILE=$(awk -F "/" '/^URL_FILE/ {print $NF}' "$SRC_FILE")
HASH_SHA256=$(awk '/^HASH_SHA256/ {print $NF}' "$SRC_FILE")

mkdir -vp "$TMPDIR"

wget "$URL_FILE" -O "$TMPDIR"/"$NAME_FILE"
CHK=$(sha256sum "$TMPDIR"/"$NAME_FILE"|grep "$HASH_SHA256")
if [ -z "$CHK" ];then exit 1;fi

cp -v "$SRC_FILE" "$TMPDIR"/"$SRC_FILE"

mv -v "$TMPDIR" "$PKG_DIR"

find "$PKG_DIR"
