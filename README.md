## **GCP Regional Cluster Auto-Scaler with Cloud SQL Management**

### **Overview**

This **smart, automated Google Cloud Function** is designed to reduce costs by scaling down GKE regional node pools, stopping Cloud SQL instances during off-hours (e.g., nighttime, weekends), and scaling them back up automatically when needed. The function can be **scheduled to run automatically** at a defined time or **manually triggered via an HTTP request**.

It intelligently detects whether **one or multiple node pools** need to be resized and **simultaneously stops or starts the associated Cloud SQL instance** based on the cluster size.

### **Features**

✅ **Smart Scaling**: Detects and resizes **single or multiple GKE regional node pools**.\
✅ **Cost Optimization**: Scales resources to **zero** when not in use and **restores them automatically** when needed.\
✅ **Cloud SQL Management**: **Stops Cloud SQL** when node pools are resized to zero, and **starts it back** when node pools are resized above zero.\
✅ **Supports Manual & Scheduled Execution**: Run via **HTTP trigger** (URL args `?size=3`) or schedule via **Cloud Scheduler**.\
✅ **Customizable with Environment Variables**: Uses **env.yaml** for easy configuration.

---

### **Setup Instructions**

### **1️⃣ Configure Environment Variables**

Before deploying, edit the `env.yaml` file with your project and cluster details:

```yaml
PROJECT_ID: "your-gcp-project-id"
REGION: "us-central1"
CLUSTER_ID: "my-gke-cluster"
NODE_POOLS: "first-pool,second-pool" # Comma-separated list of node pools
CLOUD_SQL_INSTANCE: "example-sql-instance"
```

---

### **2️⃣ Deploy the Function**

For security purposes, this function should be deployed for **authenticated users only**. Ensure that Cloud Scheduler is configured with Auth OIDC header with a service account which has **Cloud Run Invoker** and **Cloud Functions Admin** roles.

This function can be deployed via the **GCP UI Console** or using the CLI.

Or use the command in `gcloud-cli.sh` script to deploy the function:

```bash
bash gcloud-cli.sh
```

This script will deploy the function using `gcloud functions deploy` with environment variables.

---

### **3️⃣ Trigger the Function**

#### **Manual Scaling via HTTP**

You can manually **resize your cluster and manage Cloud SQL** by sending an HTTP request:

- **Resize node pools to 3 and start Cloud SQL**:

  ```bash
  curl -X GET "https://REGION-PROJECT-ID.cloudfunctions.net/resize-node-pools?size=3" \
     -H "Authorization: Bearer $(gcloud auth print-identity-token)"
  ```

- **Scale node pools to 0 and stop Cloud SQL**:

  ```bash
  curl -X GET "https://REGION-PROJECT-ID.cloudfunctions.net/resize-node-pools" -H "Authorization: Bearer $(gcloud auth print-identity-token)"
  ```

  > \*\*If no `size` is specified, the default is `0` (scale down).

---

### **4️⃣ Automate with Cloud Scheduler**

To automatically run the function at night or during off-peak hours, create a **Cloud Scheduler job**:

```bash
gcloud scheduler jobs create http scale-down-gke \
    --schedule "0 22 * * *" \
    --uri "https://REGION-PROJECT-ID.cloudfunctions.net/resize-node-pools?size=0" \
    --http-method GET
```

To **scale up in the morning**:

```bash
gcloud scheduler jobs create http scale-up-gke \
    --schedule "0 7 * * *" \
    --uri "https://REGION-PROJECT-ID.cloudfunctions.net/resize-node-pools?size=3" \
    --http-method GET
```

This will **automatically scale down at 10 PM and scale up at 7 AM** every day.

---

### **How It Works**

1. Reads configuration from `env.yaml` for **GKE cluster**, **node pools**, and **Cloud SQL**.
2. **Checks the URL parameter** `?size=`:
   - If no size is provided → **Defaults to 0** (scale down).
   - If size > 0 → **Resizes to that value**.
3. **Resizes regional GKE node pools** using `setSize()`.
4. If size == **0**, **stops Cloud SQL**.
5. If size > **0**, **starts Cloud SQL**.
6. Logs every action for easy debugging.

---

### **Final Thoughts**

This **automated GKE scaler** ensures **cost efficiency** by dynamically resizing resources.

- **Run it manually or automatically** with Cloud Scheduler.
- **Saves significant costs** when resources are idle.
- **Easy to configure** using `env.yaml`.

🚀 **Deploy now and start saving on GCP costs!**
