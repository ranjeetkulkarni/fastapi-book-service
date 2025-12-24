# 📚 Bookly API (FastAPI + Docker + Redis + Celery)

A production-ready REST API for a book review service. This project demonstrates modern backend architecture using **FastAPI**, **PostgreSQL**, **Redis**, and **Celery**, fully containerized with **Docker**.

---

## 🚀 Tech Stack & Architecture

### Core Framework
- **[FastAPI](https://fastapi.tiangolo.com/)** – High-performance Python web framework with automatic validation & OpenAPI docs.
- **[Pydantic v2](https://docs.pydantic.dev/)** – Data validation, serialization, and configuration management.

### Database & ORM
- **[PostgreSQL](https://www.postgresql.org/)** – Primary relational database.
- **[SQLModel](https://sqlmodel.tiangolo.com/)** – ORM built on SQLAlchemy + Pydantic.

### Async Tasks & Caching
- **[Redis](https://redis.io/)**
  - JWT blocklist (logout)
  - Celery message broker
  - Caching (extensible)
- **[Celery](https://docs.celeryq.dev/)**
  - Background email sending during signup
  - Non-blocking async task execution

### Authentication & Security
- **JWT (Access + Refresh tokens)**
- **Passlib (bcrypt)** – Secure password hashing
- **Security middleware** – TrustedHost, CORS

### Testing & QA
- **[Pytest](https://docs.pytest.org/)** – Unit & integration testing
- **[Schemathesis](https://schemathesis.readthedocs.io/)** – OpenAPI-based API fuzzing and crash detection

---

## 🛠️ Installation & Setup

### Option 1: Docker (Recommended)

This starts **API + PostgreSQL + Redis + Celery Worker**.

1. Create a `.env` file in the root directory (see `.env.example`)
2. Run:
   ```bash
   docker compose up --build
   ```

3. **Access:**
   - **Swagger Docs:** http://localhost:8000/docs
   - **ReDoc:** http://localhost:8000/redoc

### Option 2: Local Development

1. **Start PostgreSQL & Redis** (locally or via Docker)
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run FastAPI:**
   ```bash
   fastapi dev src/main.py
   ```

4. **Start Celery worker** (separate terminal):
   ```bash
   celery -A src.celery_tasks worker --loglevel=info
   ```

---

## 🧪 Testing

**Run Unit Tests**
```bash
pytest
```

**Run API Fuzzing (OpenAPI-based)**
```bash
st run http://127.0.0.1:8000/openapi.json --checks all
```

> **Note:** Fuzzing may report expected 400/401 errors due to invalid or unauthenticated inputs.

---

## 📂 Project Structure

```text
├── src/
│   ├── auth/                 # Authentication Module (Signup, Login, JWT)
│   ├── books/                # Book CRUD Module
│   ├── reviews/              # Review CRUD Module
│   ├── db/                   # Database Connection & Models
│   ├── tests/                # Testing Suite
│   ├── main.py               # Application Entrypoint
│   ├── config.py             # Settings Management
│   ├── celery_tasks.py       # Background Workers
│   ├── mail.py               # Email Logic
│   ├── middleware.py         # Custom Request Processing
│   └── errors.py             # Global Error Handling
├── Dockerfile                # Instructions to build the App Image
├── docker-compose.yml        # Orchestrator for App + DB + Redis
├── requirements.txt          # Python Dependencies
└── .env                      # Secrets (Not pushed to Git)
# 📚 Bookly API (FastAPI + Docker + Redis + Celery)

A production-ready REST API for a book review service. This project demonstrates modern backend architecture using **FastAPI**, **PostgreSQL**, **Redis**, and **Celery**, fully containerized with **Docker**.

---

## 🚀 Tech Stack & Architecture

### Core Framework
- **[FastAPI](https://fastapi.tiangolo.com/)** – High-performance Python web framework with automatic validation & OpenAPI docs.
- **[Pydantic v2](https://docs.pydantic.dev/)** – Data validation, serialization, and configuration management.

### Database & ORM
- **[PostgreSQL](https://www.postgresql.org/)** – Primary relational database.
- **[SQLModel](https://sqlmodel.tiangolo.com/)** – ORM built on SQLAlchemy + Pydantic.

### Async Tasks & Caching
- **[Redis](https://redis.io/)**
  - JWT blocklist (logout)
  - Celery message broker
  - Caching (extensible)
- **[Celery](https://docs.celeryq.dev/)**
  - Background email sending during signup
  - Non-blocking async task execution

### Authentication & Security
- **JWT (Access + Refresh tokens)**
- **Passlib (bcrypt)** – Secure password hashing
- **Security middleware** – TrustedHost, CORS

### Testing & QA
- **[Pytest](https://docs.pytest.org/)** – Unit & integration testing
- **[Schemathesis](https://schemathesis.readthedocs.io/)** – OpenAPI-based API fuzzing and crash detection

---

## 🛠️ Installation & Setup

### Option 1: Docker (Recommended)

This starts **API + PostgreSQL + Redis + Celery Worker**.

1. Create a `.env` file in the root directory (see `.env.example`)
2. Run:
   ```bash
   docker compose up --build

```

3. **Access:**
* **Swagger Docs:** [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)
* **ReDoc:** [http://localhost:8000/redoc](https://www.google.com/search?q=http://localhost:8000/redoc)



### Option 2: Local Development

1. **Start PostgreSQL & Redis** (locally or via Docker)
2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Run FastAPI:**
```bash
fastapi dev src/main.py

```


4. **Start Celery worker** (separate terminal):
```bash
celery -A src.celery_tasks worker --loglevel=info

```



---

## 🧪 Testing

**Run Unit Tests**

```bash
pytest

```

**Run API Fuzzing (OpenAPI-based)**

```bash
st run [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json) --checks all

```

> **Note:** Fuzzing may report expected 400/401 errors due to invalid or unauthenticated inputs.

```

---

### **2. `Workflow.md`**
Save this in your project root to document exactly how your code works.

```markdown
# 🧠 Project Workflow & Codebase Deep Dive

This document explains the architecture of `Bookly`, outlining the role of each file and how data flows through the system.

## 📂 Project Structure

```text
├── src/
│   ├── auth/                 # Authentication Module (Signup, Login, JWT)
│   ├── books/                # Book CRUD Module
│   ├── reviews/              # Review CRUD Module
│   ├── db/                   # Database Connection & Models
│   ├── tests/                # Testing Suite
│   ├── main.py               # Application Entrypoint
│   ├── config.py             # Settings Management
│   ├── celery_tasks.py       # Background Workers
│   ├── mail.py               # Email Logic
│   ├── middleware.py         # Custom Request Processing
│   └── errors.py             # Global Error Handling
├── Dockerfile                # Instructions to build the App Image
├── docker-compose.yml        # Orchestrator for App + DB + Redis
├── requirements.txt          # Python Dependencies
└── .env                      # Secrets (Not pushed to Git)

```

---

## 🔍 Detailed File Breakdown

### **1. Entrypoint & Configuration**

* **`src/main.py`**
* **Role:** The "Front Door" of the application.
* **Function:** Initializes `FastAPI()`, registers middleware, registers global error handlers (`register_all_errors`), and includes routers (`auth`, `books`, `reviews`).
* **Key Concept:** **Lifespan Events** (startup/shutdown logic) are managed here.


* **`src/config.py`**
* **Role:** The "Control Panel".
* **Function:** Uses `pydantic_settings` to read `.env` variables safely. Validates critical settings like `DATABASE_URL` and `JWT_SECRET`.
* **Key Concept:** **Type Validation** for environment variables.


* **`src/middleware.py`**
* **Role:** The "Traffic Guard".
* **Function:** Intercepts every request *before* it hits a route. Used for logging execution time (`process_time`) and managing Trusted Hosts.
* **Key Concept:** **ASGI Middleware**.


* **`src/errors.py`**
* **Role:** The "Safety Net".
* **Function:** Maps custom exceptions (e.g., `UserNotFound`) to HTTP Status Codes (e.g., `404`). Prevents the server from leaking internal stack traces (500 errors) to users.
* **Key Concept:** **Global Exception Handling**.



---

### **2. The Database Layer (`src/db/`)**

* **`src/db/main.py`**
* **Role:** The "Connection Manager".
* **Function:** Creates the SQLAlchemy `Engine` and `Session`. Provides the `get_session` dependency for routes.
* **Key Concept:** **Dependency Injection** (`Depends(get_session)`).


* **`src/db/models.py`**
* **Role:** The "Blueprints".
* **Function:** Defines database tables (`User`, `Book`, `Review`) using `SQLModel`. Handles relationships (Foreign Keys).
* **Key Concept:** **ORM (Object-Relational Mapping)**.


* **`src/db/redis.py`**
* **Role:** The "Short-term Memory".
* **Function:** Manages the connection to Redis. Specifically used for the **JTI Blocklist** (blacklisting tokens on logout).



---

### **3. Feature Modules (`auth`, `books`, `reviews`)**

Each module follows the **Controller-Service-Repository** pattern (simplified into Route-Service-Schema).

* **`routes.py` (The Controller)**
* **Function:** Defines API endpoints (`GET /books`, `POST /signup`). Accepts user input, validates it via **Schemas**, and delegates logic to the **Service**.
* **Key Concept:** **Path Operations**.


* **`schemas.py` (The Data Shape)**
* **Function:** Uses Pydantic to strictly define Input (`BookCreateModel`) and Output (`BookDetailModel`).
* **Key Concept:** **Data Validation & Serialization**. Contains `field_serializer` logic to fix Date formatting.


* **`service.py` (The Business Logic)**
* **Function:** The "Brain". Interacts with the database. Contains core logic like "Check if user exists," "Calculate hash," or "Find book by ID." Raises exceptions if operations fail.
* **Key Concept:** **Separation of Concerns**.


* **`utils.py` (Auth only)**
* **Function:** Helper functions for JWT encoding/decoding and Password hashing (`bcrypt`).
* **Key Concept:** **Cryptography**.


* **`dependencies.py` (Auth only)**
* **Function:** The "Bouncer". Verifies if a user provides a valid token before granting access to protected routes.
* **Key Concept:** **Security Dependencies** (`HTTPBearer`).



---

### **4. Background Tasks**

* **`src/celery_tasks.py`**
* **Role:** The "Worker".
* **Function:** Defines tasks that run outside the main request loop (e.g., `send_email_task`).
* **Key Concept:** **Asynchronous Processing**.


* **`src/mail.py`**
* **Role:** The "Postman".
* **Function:** uses `FastAPI-Mail` to construct and send emails via SMTP (Gmail).



---

### **5. Infrastructure**

* **`Dockerfile`**
* **Role:** The "Recipe".
* **Function:** Instructions to build the Python environment (Install Python -> Copy Code -> Install Deps -> Run App).


* **`docker-compose.yml`**
* **Role:** The "Conductor".
* **Function:** Spins up the entire stack:
1. **Web:** FastAPI App
2. **Worker:** Celery Task Runner
3. **DB:** PostgreSQL Database
4. **Redis:** Cache/Queue Broker


* **Key Concept:** **Container Orchestration**.



```

### **3. Save Your Progress (Git)**
Since you are done for today, run this to save your work securely:

```powershell
git add .
git commit -m "feat: complete backend with crash-proof auth, reviews, and fuzz testing"

```
