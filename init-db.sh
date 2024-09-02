#!/bin/bash
set -e

if [ -n "$TEST_POSTGRES_DB" ]; then
  psql -U postgres -c "CREATE DATABASE $TEST_POSTGRES_DB;"
fi