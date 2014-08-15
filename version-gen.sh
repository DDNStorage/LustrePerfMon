#!/usr/bin/env bash

DEFAULT_VERSION="0.1.g$(git rev-parse --short HEAD).ddn1"

if test -z "$VERSION"; then
	VERSION="$DEFAULT_VERSION"
fi

VERSION="`echo \"$VERSION\" | sed -e 's/-/./g'`"

echo -n "$VERSION"
