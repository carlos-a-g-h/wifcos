#!/bin/bash

set -e

SRC_FILE="sources.grub2-efi.txt"
PKG_DIR="dep.grub2-efi"
TMPDIR="_tmp"

NAME_FILE=$(awk "/NAME_FILE/" "$SRC_FILE" | sed 's/NAME_FILE //')
URL_FILE=$(awk "/URL_FILE/" "$SRC_FILE" | sed 's/URL_FILE //')
HASH_SHA256=$(awk "/HASH_SHA256/" "$SRC_FILE" | sed 's/HASH_SHA256 //')

mkdir -vp "$TMPDIR"

wget "$URL_FILE" -O "$TMPDIR"/"$NAME_FILE"
CHK=$(sha256sum "$TMPDIR"/"$NAME_FILE"|grep "$HASH_SHA256")
if [ -z "$CHK" ];then exit 1;fi

cp -v "$SRC_FILE" "$TMPDIR"/"$SRC_FILE"

mv -v "$TMPDIR" "$PKG_DIR"

find "$PKG_DIR"
