import functions_framework
import googleapiclient.discovery
import google.auth
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
PROJECT_ID = os.environ.get("PROJECT_ID", "default-project-id")
REGION = os.environ.get("REGION", "us-central1")
CLUSTER_ID = os.environ.get("CLUSTER_ID", "my-gke-cluster")
NODE_POOLS = os.environ.get(
    "NODE_POOLS", "default-pool,default-pool").split(",")  # Convert CSV to list
CLOUD_SQL_INSTANCE = os.environ.get(
    "CLOUD_SQL_INSTANCE", "default-sql-instance")

# Configure logging
logging.basicConfig(level=logging.INFO)


@functions_framework.http
def resize_node_pools_sql(request):
    """
    Cloud Function to resize multiple GKE node pools and optionally stop/start a Cloud SQL instance.
    Triggered by an HTTP request.
    """

    try:
        # Parse ARGS input from the HTTP URL input
        request_args = request.args
        size = int(request_args.get('size', 0))  # Default to 0 if not provided
        # Authenticate using the default service account of the Cloud Function
        credentials, _ = google.auth.default()
        gke_service = googleapiclient.discovery.build(
            'container', 'v1', credentials=credentials)

        print(f"Message: Resizing GKE node pools to {size} nodes.")
        logging.info(
            f"From logginf info: Resizing GKE node pools to {size} nodes.")

        gke_responses = {}
        response_message = {}

        # Step 1: Resize both GKE node pools
        for node_pool in NODE_POOLS:
            try:
                gke_request = gke_service.projects().locations().clusters().nodePools().setSize(
                    name=f"projects/{PROJECT_ID}/locations/{REGION}/clusters/{CLUSTER_ID}/nodePools/{node_pool}",
                    body={"nodeCount": size}
                )

                gke_response = gke_request.execute()
                logging.info(
                    f"Node pool '{node_pool}' resized to {size} nodes.")
                gke_responses[node_pool] = gke_response
            except Exception as e:
                logging.error(
                    f"Error resizing node pool '{node_pool}': {str(e)}")
                gke_responses[node_pool] = {"error": str(e)}

        response_message["GKE Responses"] = gke_responses

    except Exception as e:
        logging.error(f"Error resizing GKE node pools: {str(e)}")
        return {"error": f"Error resizing GKE node pools: {str(e)}"}, 500

    # Step 2: Stop or Start Cloud SQL instance based on size
    activation_policy = "ALWAYS" if size > 0 else "NEVER"

    try:
        sql_service = googleapiclient.discovery.build(
            'sqladmin', 'v1', credentials=credentials)

        sql_request = sql_service.instances().patch(
            project=PROJECT_ID,
            instance=CLOUD_SQL_INSTANCE,
            body={
                "settings": {
                    "activationPolicy": activation_policy
                }
            }
        )
        sql_response = sql_request.execute()
        logging.info(
            f"Cloud SQL instance '{CLOUD_SQL_INSTANCE}' set to activationPolicy '{activation_policy}'.")
        response_message["Cloud SQL Response"] = sql_response

    except Exception as e:
        logging.error(
            f"Error updating Cloud SQL instance '{CLOUD_SQL_INSTANCE}': {str(e)}")
        response_message["Cloud SQL Response"] = {"error": str(e)}

    return response_message, 200
