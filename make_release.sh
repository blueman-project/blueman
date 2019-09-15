#!/bin/sh

VERSION=$(git describe --tags --abbrev=0)
NAME="blueman-$VERSION"

echo "Creating tar archive"
git archive --prefix="${NAME}/" --format=tar --worktree-attributes HEAD > "${NAME}.tar"

echo "Compressing archive in xz format."
xz --force --keep "${NAME}.tar"

echo "Compressing archive in gz format."
gzip --force --keep "${NAME}.tar"

echo "Cleaning up."
rm "${NAME}.tar"
