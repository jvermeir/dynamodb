#!/usr/bin/env bash

set -o nounset
set -o pipefail
set -o errexit

if [ $# == 0 ]; then
  echo "Usage: ./tail-lambda-logs <amplify function resource>"
  exit 1
fi

aws logs tail "$0" --follow --since 1h
