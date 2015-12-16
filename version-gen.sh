#!/usr/bin/env bash

MONSYSTEM_VERSION=$(grep MONSYSTEM_VERSION ./version.h  \
        | awk '{print $3}' | tr \" " " | awk '{print $1}')
if [ -z "$BUILD_VERSION" ]; then
        MONSYSTEM_PKGVER=$MONSYSTEM_VERSION.g$(git rev-parse --short HEAD).ddn
else
        MONSYSTEM_PKGVER=$MONSYSTEM_VERSION.g$(git rev-parse --short HEAD).ddn.$BUILD_VERSION
fi

MONSYSTEM_PKGVER="`echo \"$MONSYSTEM_PKGVER\" | sed -e 's/-/./g'`"

echo -n "$MONSYSTEM_PKGVER"
