#!/bin/bash

set -e

# sudo apt-get update
# sudo apt-get install -yy sbsigntool

SRC_FILE="sources.systemd-boot.txt"
PKG_DIR="dep.systemd-boot"
TMPDIR="_tmp"

NAME_DEB1=$(awk "/NAME_DEB1/" "$SRC_FILE" | sed 's/NAME_DEB1 //')
URL_DEB1=$(awk "/URL_DEB1/" "$SRC_FILE" | sed 's/URL_DEB1 //')
SHA256_DEB1=$(awk "/SHA256_DEB1/" "$SRC_FILE" | sed 's/SHA256_DEB1 //')
TARGET_DEB1=$(awk "/TARGET_DEB1/" "$SRC_FILE" | sed 's/TARGET_DEB1 //')

NAME_DEB2=$(awk "/NAME_DEB2/" "$SRC_FILE" | sed 's/NAME_DEB2 //')
URL_DEB2=$(awk "/URL_DEB2/" "$SRC_FILE" | sed 's/URL_DEB2 //')
SHA256_DEB2=$(awk "/SHA256_DEB2/" "$SRC_FILE" | sed 's/SHA256_DEB2 //')
TARGET_DEB2=$(awk "/TARGET_DEB2/" "$SRC_FILE" | sed 's/TARGET_DEB2 //')

mkdir -vp "$TMPDIR"

wget "$URL_DEB1" -O "$TMPDIR"/"$NAME_DEB1"
CHK=$(sha256sum "$TMPDIR"/"$NAME_DEB1"|grep "$SHA256_DEB1")
if [ -z "$CHK" ];then exit 1;fi

wget "$URL_DEB2" -O "$TMPDIR"/"$NAME_DEB2"
CHK=$(sha256sum "$TMPDIR"/"$NAME_DEB2"|grep "$SHA256_DEB2")
if [ -z "$CHK" ];then exit 1;fi

bash tool_extr_deb.sh "$TMPDIR"/"$NAME_DEB1" "$TMPDIR"/deb1
if [ $? -eq 0 ];then true;else exit 1;fi

bash tool_extr_deb.sh "$TMPDIR"/"$NAME_DEB2" "$TMPDIR"/deb2
if [ $? -eq 0 ];then true;else exit 1;fi

TARGET_DEB1_PATH=$(find "$TMPDIR"/deb1 -name "$TARGET_DEB1")
TARGET_DEB2_PATH=$(find "$TMPDIR"/deb2 -name "$TARGET_DEB2")

mkdir -vp "$PKG_DIR"/systemd-boot

cp -v "$TARGET_DEB1_PATH" "$PKG_DIR"/systemd-boot
cp -v "$TARGET_DEB2_PATH" "$PKG_DIR"/systemd-boot

cp -v "$SRC_FILE" "$PKG_DIR"

bash tool_rcalc_sha256.sh "$PKG_DIR" "$PKG_DIR"/"systemd-boot.sha256.txt"

wget "http://security.ubuntu.com/ubuntu/pool/main/o/openssl/libssl3t64_3.0.13-0ubuntu3.16_amd64.deb" -O "$TMPDIR"/debx
wget "http://mirrors.kernel.org/ubuntu/pool/main/s/sbsigntool/sbsigntool_0.9.4-3.1ubuntu7_amd64.deb" -O "$TMPDIR"/debx
wget "http://security.ubuntu.com/ubuntu/pool/main/u/util-linux/libuuid1_2.39.3-9ubuntu6.6_amd64.deb" -O "$TMPDIR"/debx

sudo apt-get install -yy ./"$TMPDIR"/debx/*

sbverify --list "$PKG_DIR"/systemd-boot/"$TARGET_DEB2" > "$PKG_DIR"/systemd-boot/"$TARGET_DEB2"".sbverify.txt"

rm -rfv "$TMPDIR"
