
# Nutritional Table Detection and Information Retrieval

This project is designed to automatically detect nutritional tables from images and retrieve relevant information using Optical Character Recognition (OCR). The application is built with Python, Docker, and Google Cloud services.

## Prerequisites

Make sure you have the following installed on your local machine:

- Docker: [Download Docker](https://www.docker.com/products/docker-desktop)
- Python 3.11 or higher: [Download Python](https://www.python.org/downloads/)

Additionally, you need:

- A Google Cloud Project with access to Cloud Storage, Vertex AI, and Vision API.
- A Google Cloud Service Account with the necessary permissions to interact with these services.
- A `.env` file with the required environment variables (see below).
- The Google Cloud Service Account key file in JSON format.

## Environment Variables

Before running the project, make sure you have a `.env` file with the following details:

```bash
PROJECT_ID=<your-google-cloud-project-id>
GCS_BUCKET_NAME=<your-google-cloud-storage-bucket>
GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gcp_service_account_key.json
```

**Important:** The `GOOGLE_APPLICATION_CREDENTIALS` must point to the **path inside the Docker container**, not the local machine. This path is where the service account key will be mounted. In this case, we are using `/run/secrets/gcp_service_account_key.json`.

## Setting Up Google Cloud Service Account

1. **Create a Service Account**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Navigate to **IAM & Admin** > **Service Accounts**.
   - Create a new service account or use an existing one that has permissions to access Cloud Storage, Vertex AI, and Vision API.

2. **Download the Service Account Key**:
   - Go to the **Keys** section of your service account.
   - Create a new key in JSON format.
   - Save this key in a secure location on your local machine.

3. **Create a `secrets/` directory**:
   - Inside your project directory (or any other preferred location), create a `secrets/` directory to store your service account key.
   - Move the downloaded JSON key file into this directory

4. **Mount the Service Account Key in Docker**:
   In the Docker run command, we use the `-v` option to **mount the service account key** into the Docker container. This allows the container to access your Google Cloud credentials securely.

   For example:
   ```bash
   docker run `
     --name nutrient_extractor_app `
     -p 8000:8000 `
     --env-file .env `
     -v ./secrets/<your_service_account_name>.json:/run/secrets/gcp_service_account_key.json:ro `
     dockerimage-nutrientextractor
   ```

   - `-v ./secrets/<your_service_account_name>.json:/run/secrets/gcp_service_account_key.json:ro`: This command mounts the service account file from your local machine into the container's `/run/secrets/gcp_service_account_key.json` path.
     - `./secrets/<your_service_account_name>.json`: This is the path to the service account key file on your local machine.
     - `/run/secrets/gcp_service_account_key.json`: This is the path inside the Docker container where the key will be accessible.
     - `ro`: The `ro` flag makes the file **read-only** inside the container, which is a good security practice.

   **Ensure that the `GOOGLE_APPLICATION_CREDENTIALS` variable in your `.env` file points to `/run/secrets/gcp_service_account_key.json`, as this is the location inside the container where the key will be mounted.**

## Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/KoustubR/Automated-Nutritional-Table-Detection-and-OCR-Based-Information-Retrieval.git
   ```

2. **Create the `.env` file**:
   
   Create a `.env` file at the root of the project with the details mentioned above. You can also use the sample `.env` file included in the project and replace the placeholders with your values.

3. **Prepare the secrets folder:**

   Store your Google Cloud Service Account key in the `secrets/` folder (or any other location).

4. **Build the Docker Image:**

   Use the following command to build the Docker image:

   ```bash
   docker build -t dockerimage-nutrientextractor .
   ```

5. **Run the Docker Container:**

   Use the following command to run the container:

   ```bash
   docker run `
     --name nutrient_extractor_app `
     -p 8000:8000 `
     --env-file .env `
     -v ./secrets/<your_service_account_name>.json:/run/secrets/gcp_service_account_key.json:ro `
     dockerimage-nutrientextractor
   ```

6. **Access the Application:**

   Once the container is running, you can access the application locally at:

   ```
   http://localhost:8000/frontend/index.html
   ```


## Troubleshooting

- **Docker Errors**: Ensure that Docker is running and you have enough memory allocated to your Docker engine.
- **Google Cloud Issues**: Double-check that your Google Cloud Service Account has the necessary permissions and that your `.env` file contains the correct information.
