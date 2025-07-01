# rag-woped-integration
Integration of Retrieval Augmented Generation for WoPeD.

=======
# Table of Contents
# Inhaltsverzeichnis
1. [🚀 Getting Started](#-getting-started)
2. [📦 Requirements](#-requirements)
3. [⚙️ Local Setup](#-local-setup)
4. [🧱 Architecture Overview](#-architecture-overview)
5. [🧩 Technologies Used](#-technologies-used)
6. [Branching & Commit: Process in VS Code](#branching--commit-process-in-vs-code)
7. [Branching and commit via Terminal](#branching--commit-process-in-vs-code)


## 🚀 Getting Started

This project is a modular, testable Retrieval-Augmented Generation (RAG) API built with Flask, LangChain, and ChromaDB — structured using hexagonal architecture.

---

### 📦 Requirements

- Python 3.10+
- pip
- (Optional) Docker/Podman
- OpenAI API Key (or compatible LLM provider)

---

### ⚙️ Local Setup

1. **Clone the repository**
`git clone https://github.com/your-username/rag-api.git`

2. **Create a virtual environment**

`python -m venv venv`

`source venv/bin/activate` 

Windows: 
`source venv\Scripts\activate`

3. **Install dependencies**

pip install -r requirements.txt

# New dependecies should be added in file "requirements.txt".

4. **Run the Flask application**

python main.py

- when using the REST-API Controller, use the subdomain /rag/?query=X for adding the parameter

5. **Run using Docker (alternative)**

`docker build -t rag-api .` or `podman build -t rag-api .`

`docker run -p 5000:5000 rag-api` or `podman run -p 5000:5000 rag-api`

5. **Run with Logging**<br>
The default logging is set to `warning` and will be active automatically when starting the application. The default can be changed by setting the `LOG_LEVEL` environment variable in `app/config/config.env`.<br>

   **Flask**<br>
   `python main.py --loglevel <level>`<br>

   **Docker**<br>
   `docker run -p 5000:5000 rag-api --loglevel <level>`

   Possible values for `<level>`:<br>
   `debug`: displays all messages<br>
   `info`: displays infos, warnings, errors, and critical messages<br>
   `warning`: displays warnings, errors, and critical messages<br>
   `error`: displays errors and critical messages<br>
   `critical`: displays only critical messages<br>
   

## 🧱 Architecture Overview

This project follows a **hexagonal architecture** pattern for a clean, testable, and maintainable Retrieval-Augmented Generation (RAG) API.

### 🎯 ApplicationService - Central Entry Point

The **`ApplicationService`** is the **main entry point** and orchestrator of the entire system:
- **Technology-agnostic**: Contains only business logic, no infrastructure dependencies
- **Coordinates workflows**: PDF processing, RAG pipeline, document management
- **Delegates to domain services**: Each service handles specific business concerns
- **Singleton pattern**: Centralized access point configured in `main.py`

### 🏗️ Architecture Layers

#### 🔹 Core Layer
- **`ApplicationService.py`**: Main business orchestrator and entry point
- **`ports/`**: Abstract interfaces (DatabasePort, RAGPort, PDFLoaderPort, QueryExtractorPort)
- **`services/`**: Business logic services that handle success logging
  - `DatabaseService`: Document CRUD operations
  - `RAGService`: Retrieval & augmentation pipeline  
  - `PDFService`: Document processing workflows
  - `QueryExtractionService`: Diagram preprocessing logic

#### 🔹 Infrastructure Layer
Infrastructure adapters handle **technical implementation** and **detailed error handling**:
- **`db/`**: 
  - `DatabaseAdapter`: ChromaDB integration via LangChainClient
  - `PDFLoader`: Document parsing and chunking
- **`rag/`**: 
  - `RAGAdapter`: RAG pipeline implementation using LangChain
  - `LangchainClient`: LangChain vector operations
- **`preprocessing/`**: 
  - `BpmnQueryExtractor`: BPMN diagram processing
  - `PnmlQueryExtractor`: PNML diagram processing

#### 🔹 Presentation Layer
- **`controller/`**: REST API endpoints via Flask (`RESTController.py`)

### 🧠 Diagram Preprocessing Feature

**Key Feature**: Improves RAG search quality by extracting meaningful business terms from BPMN/PNML diagrams.

**How it works**:
1. **Detection**: Automatically detects diagram format (BPMN vs PNML)
2. **Extraction**: Extracts business-relevant text (activity names, events, etc.)
3. **Technical Filtering**: Removes technical IDs (`task_12j0pib`, `p1`, `t3`, etc.)
4. **Structural Filtering**: Removes tool/system terms (`woped`, `designer`, `start`, `end`, etc.)

**Configuration**: Set `ENABLE_DIAGRAM_PREPROCESSING=true/false` in `app/config/config.env`

### ⚙️ Configuration Management

The system is highly configurable through environment variables in `app/config/config.env`:
- **Database settings**: ChromaDB persist directory configuration
- **ChromaDB settings**: Telemetry, connection parameters
- **Document processing**: Chunk size, overlap, PDF directory
- **RAG pipeline**: Similarity threshold, result count, embedding model
- **Diagram preprocessing**: Enable/disable semantic extraction
- **Server configuration**: Host, port settings
- **Logging**: Log level configuration

See `app/config/config.env` for all available configuration options.

### 🧪 Comprehensive Test Coverage

**108 total tests** ensuring system reliability:

#### Unit Tests (`tests/unit/`)
- **Services**: Business logic testing (database, RAG, PDF, query extraction)
- **Adapters**: Infrastructure testing (LangChain, extractors, loaders)  
- **Presentation**: API endpoint validation

#### Integration Tests (`tests/integration/`)
- **End-to-End workflows**: Complete RAG pipeline, diagram preprocessing, PDF ingestion

### 🧩 Technologies Used
- **Flask** for REST API exposure and web server
- **LangChain** for RAG orchestration and document processing
- **ChromaDB** as vector database for semantic search
- **HuggingFace Transformers** for embedding models and AI/ML components
- **xml.etree.ElementTree** (Python standard library) for BPMN/PNML XML parsing
- **PyPDF** for PDF document processing and text extraction
- **pytest** for comprehensive unit and integration testing
- **Hexagonal Architecture** for clean separation of concerns and testability


## Branching & Commit: Process in VS Code
1. Create new branch
- Go to the Source Control panel (or Ctrl + Shift + G)
<div style="text-align: center;">
    <img src="https://github.com/user-attachments/assets/4c69483b-b5e6-4f2f-9f70-95eba1c7c43f" alt="Source Control Panel" width="500">
</div>

- click on the menue icon and select "Branch" --> "Create Branch"
<div style="text-align: center;">
    <img src="https://github.com/user-attachments/assets/a11b3cc0-7550-4d65-a4eb-f42490f68c36" alt="Create Branch" width="500">
</div>

- type a name for the branch and hit ENTER, you are now in the new branch
<div style="text-align: center;">
    <img src="https://github.com/user-attachments/assets/f0ce5159-4859-4fe8-9777-f73c1ff8931c" alt="switch branch" width="500">
</div>
- If you like to change between branches, click the icon which shows your current branch (here: \Test) and select the branch you would like to change to.


2. Stage changes
- If you want to save your changeslocally to your current branch go to the source panel
- select the plus-symbol to stage all your changes
<div style="text-align: center;">
    <img src="https://github.com/user-attachments/assets/40b0f390-c185-4041-98a2-4af4d09d87c8" alt="stage changes" width="500">
</div>

- enter a commit message, containing a summary of the changes you made
<div style="text-align: center;">
    <img src="https://github.com/user-attachments/assets/9c0e492a-c2bd-4505-a4cb-f2570ac2223c" alt="commit message" width="500">
</div>

- click on Commit or press Ctrl + Enter
- 
Keep in mind, that a commit only saves your changes **locally on your machine**. To make the committed changes available to other developers, you need to **push** your changes too. You can commit regularly during your work, but you don't need to push every time you made a commit.

3. Push changes
- Go to the Source Control panel
- click the menu icon
- select "Pull, Push" --> "Push"
<div style="text-align: center;">
    <img src="https://github.com/user-attachments/assets/f4489e93-3b67-4e0f-9993-a56a0dba6090" alt="push" width="500">
</div>

## Branching and commit via Terminal
1. Create new branch
- navigate to your Project-folder (if you opened your project folder with your IDE, the IDE terminal is already in the correct folder.)
- type `git checkout -b name-of-your-branch` in your terminal, this will generate a new branch

2. Commit changes 
- type `git add .` in your terminal & hit ENTER, this stages all your changes
- type `git commit -m "Your Commit message goes here"` & hit ENTER, this commits your changes locally

3. Push changes
- type `git push origin name-of-your-branch` & hit ENTER, this pushes your committed changes to the repository.
