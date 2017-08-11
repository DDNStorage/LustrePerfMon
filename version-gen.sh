#!/usr/bin/env bash

MONSYSTEM_VERSION=$(grep MONSYSTEM_VERSION ./version.h  \
        | awk '{print $3}' | tr \" " " | awk '{print $1}')

MONSYSTEM_PKGVER=$MONSYSTEM_VERSION.g$(git rev-parse --short HEAD)

echo -n "$MONSYSTEM_PKGVER"
