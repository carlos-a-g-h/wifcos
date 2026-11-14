#!/bin/bash

set -e

sudo apt-get update
sudo apt-get install -yy sbsigntool

SRC_FILE="sources.systemd-boot.txt"
PKG_DIR="dependency.systemd-boot"
TMPDIR="_tmp"

NAME_DEB1=$(awk '/NAME_DEB1/ {print $NF}' "$SRC_FILE")
URL_DEB1=$(awk '/URL_DEB1/ {print $NF}' "$SRC_FILE")
SHA256_DEB1=$(awk '/SHA256_DEB1/ {print $NF}' "$SRC_FILE")
TARGET_DEB1=$(awk '/TARGET_DEB1/ {print $NF}' "$SRC_FILE")

NAME_DEB2=$(awk '/NAME_DEB2/ {print $NF}' "$SRC_FILE")
URL_DEB2=$(awk '/URL_DEB2/ {print $NF}' "$SRC_FILE")
SHA256_DEB2=$(awk '/SHA256_DEB2/ {print $NF}' "$SRC_FILE")
TARGET_DEB2=$(awk '/TARGET_DEB2/ {print $NF}' "$SRC_FILE")

mkdir -vp "$TMPDIR"

wget "$URL_DEB1" -O "$TMPDIR"/"$NAME_DEB1"
CHK=$(sha256sum "$TMPDIR"/"$NAME_DEB1"|grep "$SHA256_DEB1")
if [ -z "$CHK" ];then exit 1;fi

wget "$URL_DEB2" -O "$TMPDIR"/"$NAME_DEB2"
CHK=$(sha256sum "$TMPDIR"/"$NAME_DEB2"|grep "$SHA256_DEB2")
if [ -z "$CHK" ];then exit 1;fi

bash TOOL_extr_deb.sh "$TMPDIR"/"$NAME_DEB1" "$TMPDIR"/deb1
if [ $? -eq 0 ];then true;else exit 1;fi

bash TOOL_extr_deb.sh "$TMPDIR"/"$NAME_DEB2" "$TMPDIR"/deb2
if [ $? -eq 0 ];then true;else exit 1;fi

TARGET_DEB1_PATH=$(find "$TMPDIR"/deb1 -name "$TARGET_DEB1")
TARGET_DEB2_PATH=$(find "$TMPDIR"/deb2 -name "$TARGET_DEB2")

mkdir -vp "$PKG_DIR"/systemd-boot

cp -v "$TARGET_DEB1_PATH" "$PKG_DIR"/systemd-boot
cp -v "$TARGET_DEB2_PATH" "$PKG_DIR"/systemd-boot

cp -v "$SRC_FILE" "$PKG_DIR"

bash TOOL_rcalc_sha256.sh "$PKG_DIR" "$PKG_DIR"/"systemd-boot.sha256.txt"

# bash TOOL_rcalc_sha256.sh "$TMPDIR"/deb1 "$PKG_DIR"/"systemd-boot.deb1.sha256.txt"

# bash TOOL_rcalc_sha256.sh "$TMPDIR"/deb2 "$PKG_DIR"/"systemd-boot.deb2.sha256.txt"

if [ -x /usr/bin/sbverify ];
then
	true;
else
	sudo apt-get update
	sudo apt.get install -yy sbsigntool
fi

sbverify --list "$PKG_DIR"/systemd-boot/"$TARGET_DEB2" > "$PKG_DIR"/systemd-boot/"$TARGET_DEB2"".sbverify.txt"

rm -rfv "$TMPDIR"
