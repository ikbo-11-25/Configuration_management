#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
sh run.sh --vfs examples/vfs/deep --startup examples/scripts/stage5.txt
sh run.sh --vfs examples/vfs/deep --startup examples/scripts/stage5-chown-error.txt --headless
sh run.sh --vfs examples/vfs/deep --startup examples/scripts/stage5-rm-error.txt --headless
sh run.sh --vfs examples/vfs/deep --startup examples/scripts/success.txt --headless
