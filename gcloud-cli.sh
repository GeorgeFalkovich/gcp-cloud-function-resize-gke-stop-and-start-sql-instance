gcloud functions deploy resize-pools-sql \
    --gen2 \
    --region=us-central1 \
    --runtime=python312 \
    --source=. \
    --entry-point=resize_node_pools \
    --trigger-http \
    --env-vars-file=env.yaml
