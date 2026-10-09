#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
sh run.sh --vfs examples/vfs/minimal --startup examples/scripts/stage2.txt --headless
sh run.sh --vfs examples/vfs/files --startup examples/scripts/stage2.txt --headless
sh run.sh --vfs examples/vfs/deep --startup examples/scripts/stage3.txt
sh run.sh --vfs missing-directory --startup examples/scripts/stage2.txt --headless
