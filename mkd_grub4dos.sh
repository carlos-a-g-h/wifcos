#!/bin/bash

set -e

sudo apt-get update
sudo apt-get install -yy p7zip p7zip-full

SRC_FILE="sources.grub4dos.txt"
PKG_DIR="dep.grub4dos"
TMPDIR="_tmp"

NAME_FILE=$(awk "/NAME_FILE/" "$SRC_FILE" | sed 's/NAME_FILE //')
URL_FILE=$(awk "/URL_FILE/" "$SRC_FILE" | sed 's/URL_FILE //')
HASH_SHA256=$(awk "/HASH_SHA256/" "$SRC_FILE" | sed 's/HASH_SHA256 //')

mkdir -vp "$TMPDIR"

wget "$URL_FILE" -O "$TMPDIR"/"$NAME_FILE"
CHK=$(sha256sum "$TMPDIR"/"$NAME_FILE"|grep "$HASH_SHA256")
if [ -z "$CHK" ];then exit 1;fi

7z x "$TMPDIR"/"$NAME_FILE" -o"$PKG_DIR"
if [ -z "$CHK" ];then exit 1;fi

rm -v "$TMPDIR"/"$NAME_FILE"

# mv -v "$TMPDIR" "$PKG_DIR"

bash tool_rcalc_sha256.sh "$PKG_DIR" "$PKG_DIR"/"grub4dos.sha256.txt"

cp -v "$SRC_FILE" "$PKG_DIR"
