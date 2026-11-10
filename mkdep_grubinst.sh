#!/bin/bash

set -e

SRC_FILE="sources.grubinst.txt"
PKG_DIR="dep.grubinst"
TMPDIR="_tmp"

URL_FILE=$(awk "/URL_FILE/" "$SRC_FILE" | sed 's/URL_FILE //')
NAME_FILE1=$(awk "/NAME_FILE1/" "$SRC_FILE" | sed 's/NAME_FILE1 //')
NAME_FILE2=$(awk "/NAME_FILE2/" "$SRC_FILE" | sed 's/NAME_FILE2 //')
HASH_SHA256=$(awk "/HASH_SHA256/" "$SRC_FILE" | sed 's/HASH_SHA256 //')

mkdir -vp "$TMPDIR"

wget "$URL_FILE" -O "$TMPDIR"/"$NAME_FILE1"
CHK=$(sha256sum "$TMPDIR"/"$NAME_FILE1"|grep "$HASH_SHA256")
if [ -z "$CHK" ];then exit 1;fi

unzip "$TMPDIR"/"$NAME_FILE1" -d "$TMPDIR"
#if [ $? -eq 0 ];then true; else exit 1;fi

PATH_FILE2=$(find "$TMPDIR" -name "$NAME_FILE2")

mkdir -vp "$PKG_DIR"/"grubinst"

unzip "$PATH_FILE2" -d "$PKG_DIR"/"grubinst"
#if [ $? -eq 0 ];then true; else exit 1;fi

bash tool_rcalc_sha256.sh "$PKG_DIR" "$PKG_DIR"/"grubinst.sha256.txt"

cp -v "$SRC_FILE" "$PKG_DIR"

