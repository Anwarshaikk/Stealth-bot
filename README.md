# **Stealth Bot \- AI-Powered Job Application Dashboard**

Stealth Bot is a comprehensive, AI-powered dashboard designed to streamline and automate the job application process for recruitment agencies or power users. It leverages modern AI services to parse resumes, matches candidates to relevant job listings, and automates the application process.

## **✨ Features**

* **📄 Intelligent Resume Upload**: Drag-and-drop resumes (PDF/DOCX) for immediate processing.  
* **🧠 Dynamic AI Parsing**: Choose between multiple parsing engines on the fly:  
  * pyresparser (fast, local)  
  * Google Document AI (highly accurate, cloud-based)  
  * OpenAI GPT-4 (state-of-the-art, flexible)  
* **🤖 Automated Job Matching**: Scrapes job boards like Indeed.com to find relevant positions based on candidate skills.  
* **⭐ AI-Powered Job Ranking**: Uses OpenAI embeddings to calculate a relevance score (0-100%) for each job match.  
* **⚙️ Asynchronous Application Bot**: Submits job applications in the background using a robust Playwright worker.  
  * Includes site-specific handlers for platforms like Indeed and LinkedIn.  
  * Reports detailed statuses (submitted, manual\_required, failed).  
* \*\* Kanban Application Tracker\*\*: A drag-and-drop board to visually track the status of all submitted applications (Applied, Interview, Offer, Rejected).  
* **🔧 Centralized Settings**: Manage API keys and select the preferred resume parser from the UI.  
* **🔔 Real-time Notifications**: A polished toast notification system provides instant user feedback.

## **🏗️ Architecture**

The application is built with a modern, decoupled architecture, containerized for easy deployment and scalability.

* **Frontend**: A responsive **React** application built with TypeScript and styled with **TailwindCSS**.  
* **Backend**: A high-performance **FastAPI** server that exposes a RESTful API for all application logic.  
* **Worker**: A separate **Python RQ (Redis Queue)** worker that handles long-running, asynchronous tasks like submitting job applications with Playwright.  
* **Database/Cache**: **Redis** is used as both a message broker for the task queue and a primary data store/cache for candidates, applications, and settings.  
* **Containerization**: The entire stack (frontend, backend, worker, Redis) is managed via **Docker** and **Docker Compose**.

## **🚀 Getting Started**

Follow these instructions to get the entire application running locally for development or testing.

### **Prerequisites**

* [Docker](https://www.docker.com/get-started)  
* [Docker Compose](https://docs.docker.com/compose/install/)

### **1\. Environment Variables**

Before you can run the application, you must set up the necessary environment variables.

Create a file named .env in the root of the project directory. Copy the contents of .env.example below and fill in your own API keys and configuration.

\# .env.example

\# \-- Core Configuration \--  
\# The URL for Redis, used by the API and the worker  
REDIS\_URL=redis://redis:6379/0

\# \-- OpenAI API Key (Required for GPT-4 Parser & Job Ranking) \--  
\# Get yours from https://platform.openai.com/api-keys  
OPENAI\_API\_KEY="sk-..."

\# \-- Google Document AI Configuration (Optional, for DocAI Parser) \--  
\# Your Google Cloud Project ID  
GOOGLE\_CLOUD\_PROJECT="your-gcp-project-id"

\# The Processor ID for your Document AI instance  
GOOGLE\_DOCAI\_PROCESSOR\_ID="your-docai-processor-id"

\# The location of your processor (e.g., "us" or "eu")  
GOOGLE\_CLOUD\_LOCATION="us"

\# You must also have Google Cloud credentials configured.  
\# The recommended way is to download a service account JSON key and set its path:  
\# GOOGLE\_APPLICATION\_CREDENTIALS="/path/to/your/gcp-credentials.json"  
\# This path needs to be mounted into the Docker container (see docker-compose.yml).

### **2\. Build and Run with Docker Compose**

Once your .env file is configured, you can start the entire application stack with two commands:

\# 1\. Build the images for the API and worker services  
docker-compose build

\# 2\. Start all services in detached mode  
docker-compose up \-d

### **3\. Accessing the Application**

* **Frontend UI**: Open your browser and navigate to http://localhost:3000  
* **Backend API Docs**: The FastAPI interactive documentation (Swagger UI) is available at http://localhost:8000/docs

## **🛠️ Development & Tooling**

### **Dependency Management**

The Python backend uses pip-tools for precise dependency pinning.

* To add or change a direct dependency, edit the requirements.in file.  
* To update the pinned requirements.txt file, run:  
  pip-compile requirements.in \-o requirements.txt

### **Running Checks and Tests**

We have implemented a script to ensure code quality and prevent build failures. Before committing code, run this script from the project root:

\# Make sure the script is executable  
chmod \+x run\_checks.sh

\# Run all checks  
./run\_checks.sh

This script will:

1. Check import sorting with isort.  
2. Lint the code with flake8.  
3. Attempt a fresh docker-compose build to catch any container build issues.

To run the pytest suite directly:

docker-compose exec api pytest  
