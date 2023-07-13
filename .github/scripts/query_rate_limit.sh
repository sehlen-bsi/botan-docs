#!/bin/bash

# This script queries the current GitHub API rate limit and makes
# it available to consecutive actions as environment variables

read_limit() {
    local limit_json="$1"
    local limit_filter="$2"
    echo "$limit_json" | jq "$limit_filter"
}

limits="$(gh api rate_limit)"

remaining=$(read_limit "$limits" ".resources.core.remaining")
used=$(read_limit "$limits" ".resources.core.used")
limit=$(read_limit "$limits" ".resources.core.limit")
exceeded=$(test $remaining -eq 0 && echo 'true' || echo 'false')

echo "API_RATE_LIMIT_REMAINING=$remaining" >> $GITHUB_ENV
echo "API_RATE_LIMIT_USED=$used" >> $GITHUB_ENV
echo "API_RATE_LIMIT=$limit" >> $GITHUB_ENV
echo "API_RATE_LIMIT_EXCEEDED=$exceeded" >> $GITHUB_ENV
