#!/usr/bin/env bash

TS=$(date +%Y%m%d%H%M%S)
MONSYSTEM_VERSION=$(grep MONSYSTEM_VERSION ./version.h  \
        | awk '{print $3}' | tr \" " " | awk '{print $1}')

MONSYSTEM_PKGVER=$MONSYSTEM_VERSION.${TS}

echo -n "$MONSYSTEM_PKGVER"
