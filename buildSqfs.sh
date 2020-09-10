#!/bin/bash

# Usage: ./buildSqfs.sh <output filename> <extra files>
# NOTE: Must run in the directory it is situated in.
# This file build a squashfs image for the guest VM to use.

output="$1"
if [[ "$output" == "" ]]; then
    output="./guest.sqfs"
fi

extra="$2"
if [[ "$extra" == "" ]]; then
    extra="./extra"
fi

function die {
    echo "$1"
    exit 1
}

instanceName=`uuidgen`
tmpDir="/tmp/${instanceName}"
mkdir -p "$tmpDir"

echo "Using ${tmpDir}"

# Prepare the guest agent source
pushd guest_agent > /dev/null
make || die "Failed to prepare guest agent source"
popd > /dev/null

mkdir -p "${tmpDir}"

cp -pR guest_agent/* "${tmpDir}/." || die "Failed to copy guest agent"

if ! [[ -d "$extra" ]]; then
    echo "$extra not directory, ignoring"
else
    cp -pR "${extra}/"* "${tmpDir}/." || die "Failed to copy extra files"
fi

rm -rf "${tmpDir}/__pycache__"

rm -f "${output}"
mksquashfs ${tmpDir}/* "${output}" -all-root || die "Failed to make squashfs"

rm -rf "${tmpDir}"
