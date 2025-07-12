docker compose run --rm ray-client \
  --address=http://ray-head:8265 \
  --working-dir /app \
  --entrypoint "python app.py" \
  --runtime-env-json='{
    "env_vars": {
      "START_NUMBER": "600000",
      "NUM_BATCHES": "10",
      "BATCH_SIZE": "10000"
    }
  }'
1