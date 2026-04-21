#!/usr/bin/env bash

set -u

source "quantium_simulation/bin/activate"

if pytest tests; then
    exit 0
fi

exit 1
