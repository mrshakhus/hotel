#!/bin/bash
set -e

# Создание пользователя и базы данных, используя нестандартные переменные окружения
# if [ -n "$TEST_POSTGRES_USER" ] && [ -n "$TEST_POSTGRES_PASSWORD" ]; then
#   psql -U postgres -c "CREATE USER $TEST_POSTGRES_USER WITH PASSWORD '$TEST_POSTGRES_PASSWORD';"
# fi

if [ -n "$TEST_POSTGRES_DB" ]; then
  psql -U postgres -c "CREATE DATABASE $TEST_POSTGRES_DB;"
fi