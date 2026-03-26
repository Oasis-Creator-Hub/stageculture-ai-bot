#!/bin/bash
set -a
source .env
set +a
exec python3 app.py
