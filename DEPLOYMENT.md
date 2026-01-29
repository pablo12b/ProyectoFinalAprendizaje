# Deploying to Google Cloud Run

This guide explains how to deploy the `business_backend` service to Google Cloud Run.

## Prerequisites

1.  **Google Cloud SDK**: Ensure `gcloud` is installed and initialized.
2.  **Project ID**: Have a Google Cloud Project ID ready.
3.  **Permissions**: Ensure you have permissions to build using Cloud Build and deploy to Cloud Run.

## Step 1: Set Variables

Open your terminal and set these variables for convenience:

```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export APP_NAME="business-backend"
export REPO_NAME="business-backend-repo" # Artifact Registry Repo Name
```

## Step 2: Configure Authentification

```bash
gcloud auth login
gcloud config set project $PROJECT_ID
```

## Step 3: Enable APIs (One-time setup)

Enable necessary Google Cloud APIs:

```bash
gcloud services enable artifactregistry.googleapis.com run.googleapis.com cloudbuild.googleapis.com
```

## Step 4: Create Artifact Registry Repository (One-time setup)

If you don't have a Docker repository in Artifact Registry yet:

```bash
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for Business Backend"
```

## Step 5: Build and Push Docker Image

We use Cloud Build to build the image remotely and push it to Artifact Registry.

```bash
gcloud builds submit --tag "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$APP_NAME:latest" .
```

*Note: This command uploads the current directory context to Cloud Build, builds using the Dockerfile, and pushes the image to the specified tag.*

## Step 6: Deploy to Cloud Run

Deploy the container. **Crucial**: You need to provide the database connection string and other secrets as environment variables.

> **Warning**: For production, use **Google Secret Manager** for sensitive values like `PG_URL` and `OPENAI_API_KEY`. The example below uses plain environment variables for simplicity.

```bash
gcloud run deploy $APP_NAME \
    --image "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$APP_NAME:latest" \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars="pg_url=YOUR_PRODUCTION_DB_URL,openai_api_key=YOUR_KEY,environment=production,log_level=INFO"
```

### Important Settings:
- `--allow-unauthenticated`: Makes the API public. Remove this if you want to control access via IAM.
- `--port 8080`: Cloud Run expects the container to listen on the port defined by the `PORT` env var (default 8080).

## Step 7: Verification

After deployment, Google Cloud will provide a **Service URL**.

1.  **Health Check**:
    ```bash
    curl https://<YOUR-SERVICE-URL>/health
    ```
2.  **List Computers**:
    ```bash
    curl https://<YOUR-SERVICE-URL>/api/computers
    ```

## Database Considerations

The `pgvector` database is currently running in a local Docker container. For Cloud Run deployment, you have two main options:

1.  **Cloud SQL for PostgreSQL**: The recommended production approach. You will need to enable the `vector` extension in Cloud SQL.
2.  **Self-Hosted PostgreSQL**: Connect to a VM or another provider ensuring it's accessible from Cloud Run.

**Ensure to update the `PG_URL` environment variable in the deploy command to point to your production database.**
