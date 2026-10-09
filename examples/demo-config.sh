#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
sh run.sh --vfs examples/vfs/deep --startup examples/scripts/stage2.txt
sh run.sh --vfs examples/vfs/deep --startup examples/scripts/stage2-error.txt --headless
sh run.sh --vfs examples/vfs/deep --startup missing.txt --headless
sh run.sh --unknown
