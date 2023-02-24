#!/bin/bash

flake8 "cs/ratelimit" --count --exit-zero --max-complexity=15 --max-line-length=127 --statistics
pylint "cs/ratelimit" --exit-zero --max-line-length=127 --disable=R0801 --ignore=tests
pydocstyle "cs/ratelimit" --count