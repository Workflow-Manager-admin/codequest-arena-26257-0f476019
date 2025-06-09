#!/bin/bash
cd /home/kavia/workspace/code-generation/codequest-arena-26257-0f476019/codequest_arena
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

