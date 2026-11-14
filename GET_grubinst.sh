#!/bin/bash

set -ex

SRC_FILE="sources.grubinst.txt"
PKG_DIR="dependency.grubinst"
TMPDIR="_tmp"

#URL_FILE=$(awk "/URL_FILE/" "$SRC_FILE" | sed 's/URL_FILE //')
#NAME_FILE1=$(awk "/NAME_FILE1/" "$SRC_FILE" | sed 's/NAME_FILE1 //')
#NAME_FILE2=$(awk "/NAME_FILE2/" "$SRC_FILE" | sed 's/NAME_FILE2 //')
#HASH_SHA256=$(awk "/HASH_SHA256/" "$SRC_FILE" | sed 's/HASH_SHA256 //')

COMMIT=$(awk -F "/" '/^URL_COMMIT/ {print $NF}' "$SRC_FILE")
if [ -z $COMMIT ];then exit 1;fi

URL_FILE=$(awk '/^URL_FILE/ {print $NF}' "$SRC_FILE")
if [ -z $URL_FILE ];then exit 1;fi

NAME_FILE=$(awk '/^NAME_FILE/ {print $NF}' "$SRC_FILE")
if [ -z $NAME_FILE ];then exit 1;fi

HASH_SHA256=$(awk '/^HASH_SHA256/ {print $NF}' "$SRC_FILE")
if [ -z $HASH_SHA256 ];then exit 1;fi

mkdir -vp "$TMPDIR"

PATH_TMP="$TMPDIR"/grubutils.zip
wget "$URL_FILE" -O "$PATH_TMP"
CHK=$(sha256sum "$PATH_TMP"|grep "$HASH_SHA256")
if [ -z "$CHK" ];then exit 1;fi

unzip "$PATH_TMP" -d "$TMPDIR"
rm -v "$PATH_TMP"

DIR_EX=$(ls "$TMPDIR")
mv -v "$TMPDIR"/"$DIR_EX" "$TMPDIR"/grubutils

PATH_FILE=$(find "$TMPDIR" -name "$NAME_FILE")

echo "$PATH_FILE"

mkdir -vp "$PKG_DIR"/grubinst

unzip "$PATH_FILE" -d "$PKG_DIR"/grubinst

bash TOOL_rcalc_sha256.sh "$PKG_DIR" "$PKG_DIR"/"grubinst.sha256.txt"

# bash TOOL_rcalc_sha256.sh "$TMPDIR" "$PKG_DIR"/"grubutils.sha256.txt"

cp -v "$SRC_FILE" "$PKG_DIR"

