#!/usr/bin/env bash
# Stop the Ralph loop and everything the current iteration spawned.
# The iteration in progress is abandoned: its uncommitted changes stay in the tree.
cd "$(git rev-parse --show-toplevel)"
[[ -f .ralph/loop.pid ]] && kill -TERM "$(cat .ralph/loop.pid)" 2>/dev/null
[[ -f .ralph/iteration.pgid ]] && kill -TERM -- "-$(cat .ralph/iteration.pgid)" 2>/dev/null
sleep 2
[[ -f .ralph/iteration.pgid ]] && kill -KILL -- "-$(cat .ralph/iteration.pgid)" 2>/dev/null
rm -f .ralph/loop.pid .ralph/iteration.pgid
echo "Ralph loop stopped. Check 'git status' for the abandoned iteration's changes."
