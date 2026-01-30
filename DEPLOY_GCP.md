# Deploy to Google Cloud Run

To deploy this application to Google Cloud Run, follow these steps:

### 1. Prerequisites
- [Google Cloud Account](https://console.cloud.google.com/)
- [Google Cloud CLI (gcloud)](https://cloud.google.com/sdk/docs/install) installed and initialized.
- **Billing enabled** for your GCP project.
- **Gemini API Key**: You must have a Gemini API key set in your secrets or environment.

### 2. Enable Required APIs
Run the following command to enable the necessary APIs:
```bash
gcloud services enable run.googleapis.com \
                       containerregistry.googleapis.com \
                       cloudbuild.googleapis.com
```

### 3. Deploy using Cloud Build
The easiest way is to use the `cloudbuild.yaml` file I created:
```bash
gcloud builds submit --config cloudbuild.yaml .
```

### 4. Alternative: Manual Deployment
If you prefer manual steps:
1. **Build and Tag**:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/welfare-agentic-ai
   ```
2. **Deploy**:
   ```bash
   gcloud run deploy welfare-agentic-ai \
     --image gcr.io/YOUR_PROJECT_ID/welfare-agentic-ai \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GOOGLE_API_KEY=AIzaSy...your_key_here
   ```

### 5. Notes
- **Security**: Hardcoded API keys have been removed. The application now expects the `GOOGLE_API_KEY` to be provided via environment variables.
