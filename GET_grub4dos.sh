#!/bin/bash

set -e

SRC_FILE="sources.grub4dos.txt"
PKG_DIR="dependency.grub4dos"
TMPDIR="_tmp"

URL_FILE=$(awk '/^URL_FILE/ {print $NF}' "$SRC_FILE")
NAME_FILE=$(awk -F "/" '/^URL_FILE/ {print $NF}' "$SRC_FILE")
HASH_SHA256=$(awk '/^HASH_SHA256/ {print $NF}' "$SRC_FILE")

mkdir -vp "$TMPDIR"

wget "$URL_FILE" -O "$TMPDIR"/"$NAME_FILE"
CHK=$(sha256sum "$TMPDIR"/"$NAME_FILE"|grep "$HASH_SHA256")
if [ -z "$CHK" ];then exit 1;fi

if [ -x /usr/bin/7x ]
then
	true
else
	sudo apt-get update
	sudo apt-get install -yy p7zip p7zip-full
fi
7z x "$TMPDIR"/"$NAME_FILE" -o"$PKG_DIR"
if [ -z "$CHK" ];then exit 1;fi

rm -v "$TMPDIR"/"$NAME_FILE"

DIR_EX=$(ls "$PKG_DIR")
mv -v "$PKG_DIR"/"$DIR_EX" "$PKG_DIR"/grub4dos

bash TOOL_rcalc_sha256.sh "$PKG_DIR" "$PKG_DIR"/"grub4dos.sha256.txt"

cp -v "$SRC_FILE" "$PKG_DIR"
