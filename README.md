# Chatbot_CV
A chatbot that asks and answers questions about information from a user's CV

## 📋 Overview

This project implements a full-stack application featuring:

- A FastAPI backend with LangGraph for conversational AI
- A Streamlit ui for chat interface
- Vector storage using Qdrant for semantic search capabilities
- Docker for containerization and easy deployment

## ⚙️ Components

### Backend

- **FastAPI Application**: REST API with structured routes
- **LangGraph Integration**: Manages conversation flow and agent interactions
- **OpenAI Integration**: Leverages OpenAI for natural language processing
- **Vector Storage**: Uses Qdrant for semantic search and retrieval

### Frontend

- **Streamlit ui**: The user interface is built with Streamlit, providing an intuitive and interactive experience directly in the browser.

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
-  OpenAI API key
- Qdrant instance (self-hosted or cloud)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Chatbot_RAG
   ```

2. Set up environment variables:
   ```bash
   cp .env.template .env
   ```

   Edit the `.env` file with your API keys and configuration

3. Start the application using docker compose:
    ```
    docker compose up --build
    ```
## 🏗️ Project Structure
    ```
    ├── chatbot                         # Backend FastAPI application
    │   ├── api/                        # API routes and helpers
    │   ├── app/                        # Core app services and configs
    │   ├── Dockerfile                  # Dockerfile for backend container
    │   ├── domain/                     # Core entities and business logic
    │   ├── infrastructure/             # Infrastructure components
    │   ├── main.py                     # Entry point for FastAPI service
    │   ├── requirements.txt            # Python dependencies for backend
    │   ├── shared/                     # Shared utilities and configs
    │   └── tests/                      # integration tests
    ├── data                            # Data storage
    │   ├── convert/                    # Data conversion scripts
    │   └── raw/                        # Unprocessed data files
    ├── docker-compose.yml              # Docker Compose config for orchestrating services
    ├── frontend                        # Frontend application
    │   ├── app.py                      # Main script for frontend service
    │   ├── Dockerfile                  # Dockerfile for frontend container
    │   └── requirements.txt            # Python dependencies for frontend
    ├── README.md                       # Project documentation
    └── test.ipynb                      # Jupyter notebook for testing
    ```

## 💻 Usage

Once the application is running:

1. Access the frontend at: http://localhost:8501
2. The backend API is available at: http://localhost:5000

## 🔧 Dependencies

### Backend
- FastAPI
- LangGraph
- LangChain
- Uvicorn
- Qdrant Client
- OpenAI

### Frontend
- Streamlit
