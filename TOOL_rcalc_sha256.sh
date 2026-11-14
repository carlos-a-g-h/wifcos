#!/bin/bash

TGTDIR="$1"

CHKFILE="$2"

CONTENTS=$(find "$TGTDIR")

echo "SHA256 HASHES
" > "$CHKFILE"

for FSE in ${CONTENTS[@]}
do
	if [ -d "$FSE" ];then continue;fi
	sha256sum "$FSE" >> "$CHKFILE"
done
