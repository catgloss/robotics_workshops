#!/bin/sh

# Abort on any error (including if wait-for-it fails).
set -e

# Wait for the backend to be up, if we know where it is.
if [ -n "$CUSTOMERS_HOST" ]; then
  .wait-for-it.sh --timeout=30 "$CUSTOMERS_HOST:${CUSTOMERS_PORT:-5672}" -- echo "rabbitmq is up"
fi

# Run the main container command.
exec "$@"