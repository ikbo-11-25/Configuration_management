#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
sh run.sh --vfs examples/vfs/deep --startup examples/scripts/stage4.txt
sh run.sh --vfs examples/vfs/deep --startup examples/scripts/stage4-cal-error.txt --headless
sh run.sh --vfs examples/vfs/deep --startup examples/scripts/stage4-ls-error.txt --headless
