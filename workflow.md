# 🧠 Bookly – Project Workflow & Architecture Deep Dive

This document provides an **in-depth explanation** of the internal architecture, file responsibilities, design patterns, and request flow of the Bookly backend. Use this as a reference when analyzing or building FastAPI projects.

---

## 🏗️ Architecture Overview

**Pattern Used:** Clean Architecture with Domain-Driven Design (DDD) principles
- **Layered Architecture:** Presentation → Business Logic → Data Access
- **Dependency Injection:** FastAPI's built-in DI system for session management, authentication
- **Repository Pattern:** Service layer abstracts database operations
- **Background Task Processing:** Celery for asynchronous operations

**Key Principles:**
- Separation of Concerns (SoC)
- Single Responsibility Principle (SRP)
- Dependency Inversion Principle (DIP)

---

## 📂 Project Structure

```text
├── src/
│   ├── auth/                 # 🔐 Authentication Module
│   │   ├── __init__.py
│   │   ├── routes.py         # HTTP endpoints (signup, login, logout, refresh)
│   │   ├── schemas.py        # Pydantic models for request/response validation
│   │   ├── service.py        # Business logic (user creation, token generation)
│   │   ├── utils.py          # JWT encoding/decoding, password hashing
│   │   └── dependencies.py   # Auth guards (verify tokens, check permissions)
│   │
│   ├── books/                # 📚 Book Management Module
│   │   ├── __init__.py
│   │   ├── routes.py         # CRUD endpoints for books
│   │   ├── schemas.py        # Book validation models
│   │   ├── service.py        # Book business logic
│   │   └── book_data.py      # Sample data/fixtures
│   │
│   ├── reviews/              # ⭐ Review Module
│   │   ├── __init__.py
│   │   ├── routes.py         # Review CRUD endpoints
│   │   ├── schemas.py        # Review validation models
│   │   └── service.py        # Review business logic
│   │
│   ├── db/                   # 🗄️ Database Layer
│   │   ├── __init__.py
│   │   ├── main.py           # DB engine, session factory, dependency
│   │   ├── models.py         # SQLModel table definitions (User, Book, Review)
│   │   └── redis.py          # Redis connection & JTI blocklist
│   │
│   ├── tests/                # 🧪 Test Suite
│   │   ├── __init__.py
│   │   ├── conftest.py       # Pytest fixtures (test client, test DB)
│   │   ├── test_books.py     # Book API tests
│   │   └── test_service.py   # Service layer unit tests
│   │
│   ├── main.py               # 🚪 Application Entrypoint
│   ├── config.py             # ⚙️ Configuration Management
│   ├── celery_tasks.py       # 🔄 Background Task Definitions
│   ├── mail.py               # 📧 Email Service
│   ├── middleware.py         # 🛡️ Custom Middleware
│   └── errors.py             # ❌ Global Exception Handling
│
├── alembic/                  # 📦 Database Migrations
│   ├── versions/             # Migration scripts
│   └── env.py                # Alembic configuration
│
├── Dockerfile                # 🐳 Container Build Instructions
├── docker-compose.yml        # 🎼 Multi-Container Orchestration
├── requirements.txt          # 📋 Python Dependencies
├── pytest.ini                # 🧪 Pytest Configuration
├── alembic.ini               # 📦 Alembic Configuration
└── .env                      # 🔒 Environment Variables (Not in Git)
```

---

## 🔍 Deep Dive: Core Files & Their Responsibilities

### 1️⃣ **Application Entrypoint & Configuration**

#### `src/main.py` - The Application Factory
**Purpose:** Central hub that assembles all application components

**What it does:**
```python
# 1. Creates the FastAPI instance
app = FastAPI(
    title="Bookly API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 2. Registers middleware (order matters!)
app.add_middleware(TrustedHostMiddleware)
app.add_middleware(CORSMiddleware)
app.add_middleware(CustomTimingMiddleware)

# 3. Registers global exception handlers
register_all_errors(app)

# 4. Includes routers from different modules
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(book_router, prefix="/books", tags=["Books"])
app.include_router(review_router, prefix="/reviews", tags=["Reviews"])

# 5. Defines lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB, Redis connections
    yield
    # Shutdown: Close connections
```

**Key Concepts:**
- **Application Factory Pattern:** Allows creating multiple app instances (testing vs production)
- **Lifespan Events:** Manage resources (DB connections, Redis pools) properly
- **Router Composition:** Each module is independent and pluggable

**What to check in other FastAPI projects:**
- ✅ How are routers organized? (by feature vs by resource)
- ✅ Is middleware order correct? (Security → Logging → Error Handling)
- ✅ Are there lifespan events for resource management?
- ✅ Is OpenAPI documentation properly configured?

---

#### `src/config.py` - Configuration Management
**Purpose:** Centralized, type-safe configuration using Pydantic Settings

**What it does:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Email
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str
    
    class Config:
        env_file = ".env"  # Reads from .env file
        case_sensitive = False
```

**Key Concepts:**
- **Type Safety:** Pydantic validates types at startup (fail fast)
- **Environment Variables:** 12-Factor App methodology
- **Default Values:** Sensible defaults for development
- **Validation:** Raises errors if required variables are missing

**What to check in other FastAPI projects:**
- ✅ Is `pydantic-settings` used for config management?
- ✅ Are sensitive values (secrets) stored in `.env` and not committed to Git?
- ✅ Are there different configs for dev/staging/prod?
- ✅ Is validation strict enough?

---

#### `src/middleware.py` - Request/Response Interceptors
**Purpose:** Cross-cutting concerns that apply to ALL requests

**What it does:**
```python
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

**Types of Middleware:**
1. **Security:** TrustedHost, CORS, CSRFProtect
2. **Logging:** Request/response logging, timing
3. **Rate Limiting:** Throttle requests per user/IP
4. **Authentication:** Global auth checks (though prefer dependencies)

**Key Concepts:**
- **ASGI Middleware Stack:** Executes in order before reaching routes
- **Request → Middleware Chain → Route → Middleware Chain → Response**
- **Middleware vs Dependencies:** Use middleware for ALL requests, dependencies for specific routes

**What to check in other FastAPI projects:**
- ✅ Is there custom middleware? What does it do?
- ✅ Are security headers set? (CORS, CSP, X-Frame-Options)
- ✅ Is request timing/logging implemented?
- ✅ Are rate limits enforced?

---

#### `src/errors.py` - Global Exception Handling
**Purpose:** Centralized error handling to prevent 500 crashes and provide consistent error responses

**What it does:**
```python
# Define custom exceptions
class BookNotFound(Exception):
    """Raised when a book doesn't exist"""
    pass

class InvalidCredentials(Exception):
    """Raised when login fails"""
    pass

# Map exceptions to HTTP responses
@app.exception_handler(BookNotFound)
async def book_not_found_handler(request: Request, exc: BookNotFound):
    return JSONResponse(
        status_code=404,
        content={"error": "Book not found", "detail": str(exc)}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the error
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    # Return generic 500 without exposing internals
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
```

**Key Concepts:**
- **Domain-Specific Exceptions:** Better than generic `ValueError`
- **Error Hiding:** Never expose stack traces in production
- **Consistent Error Format:** Clients can parse errors uniformly
- **Logging:** All errors should be logged for debugging

**What to check in other FastAPI projects:**
- ✅ Are custom exceptions defined for domain errors?
- ✅ Is there a global exception handler for uncaught errors?
- ✅ Are errors logged properly?
- ✅ Do error responses follow a consistent format?

---

### 2️⃣ **Database Layer (`src/db/`)**

#### `src/db/main.py` - Database Connection & Session Management
**Purpose:** Create and manage database connections using SQLAlchemy

**What it does:**
```python
from sqlmodel import create_engine, Session

# Create engine (connection pool)
engine = create_engine(
    Config.DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    pool_pre_ping=True,  # Verify connections before use
    pool_size=10,  # Max connections
    max_overflow=20  # Extra connections under load
)

# Dependency for routes
async def get_session():
    """Provides a DB session to routes"""
    with Session(engine) as session:
        yield session
        # Session automatically commits or rolls back
```

**Key Concepts:**
- **Connection Pooling:** Reuse connections instead of creating new ones
- **Dependency Injection:** Routes receive sessions via `Depends(get_session)`
- **Automatic Transactions:** SQLModel handles commit/rollback
- **Context Manager:** `with` statement ensures proper cleanup

**What to check in other FastAPI projects:**
- ✅ Is connection pooling configured?
- ✅ Are sessions properly closed (via context managers or dependencies)?
- ✅ Is there a health check endpoint to verify DB connectivity?
- ✅ Are migrations handled (Alembic)?

---

#### `src/db/models.py` - ORM Table Definitions
**Purpose:** Define database schema using Python classes (SQLModel)

**What it does:**
```python
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(default="user")  # "user" or "admin"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    books: List["Book"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(back_populates="user")

class Book(SQLModel, table=True):
    __tablename__ = "books"
    
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(index=True)
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: uuid.UUID = Field(foreign_key="users.uid")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(back_populates="book", cascade_delete=True)

class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    rating: int = Field(ge=1, le=5)  # 1-5 stars
    review_text: str
    book_uid: uuid.UUID = Field(foreign_key="books.uid")
    user_uid: uuid.UUID = Field(foreign_key="users.uid")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    book: Book = Relationship(back_populates="reviews")
    user: User = Relationship(back_populates="reviews")
```

**Key Concepts:**
- **Declarative Models:** Classes = Tables
- **Relationships:** `Relationship()` defines foreign keys
- **Indexes:** Speed up queries on frequently searched columns
- **Constraints:** `unique=True`, `ge=1, le=5` enforce data integrity
- **Cascade Delete:** When a book is deleted, its reviews are too

**What to check in other FastAPI projects:**
- ✅ Are models using SQLModel or SQLAlchemy Core?
- ✅ Are relationships properly defined?
- ✅ Are indexes created on frequently queried columns?
- ✅ Are constraints enforced (unique, not null, check)?
- ✅ Are timestamps (created_at, updated_at) tracked?

---

#### `src/db/redis.py` - Caching & Token Blocklist
**Purpose:** Manage Redis connection for caching and JWT invalidation

**What it does:**
```python
import redis.asyncio as redis

redis_client = redis.from_url(
    f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}",
    decode_responses=True
)

async def add_jti_to_blocklist(jti: str, expiry: int):
    """Add revoked token to blocklist"""
    await redis_client.setex(
        name=f"blocklist:{jti}",
        time=expiry,
        value="revoked"
    )

async def is_jti_blocklisted(jti: str) -> bool:
    """Check if token is revoked"""
    result = await redis_client.get(f"blocklist:{jti}")
    return result is not None
```

**Use Cases:**
1. **JWT Blocklist:** Logout invalidates tokens
2. **Caching:** Store frequently accessed data (book lists, user profiles)
3. **Rate Limiting:** Track request counts per user/IP
4. **Session Storage:** Alternative to DB for temporary data

**Key Concepts:**
- **In-Memory Storage:** Fast reads/writes
- **TTL (Time To Live):** Keys auto-expire
- **Pub/Sub:** Real-time messaging (not used here)

**What to check in other FastAPI projects:**
- ✅ Is Redis used? For what purpose?
- ✅ Are keys properly namespaced? (`blocklist:`, `cache:`)
- ✅ Are TTLs set to avoid memory leaks?
- ✅ Is Redis connection pooling configured?

---

### 3️⃣ **Feature Modules (auth, books, reviews)**

Each module follows **Clean Architecture** with clear layer separation:

#### **Layer 1: `routes.py` - Presentation Layer (HTTP Interface)**
**Purpose:** Handle HTTP requests/responses, delegate to service layer

**What it does:**
```python
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

router = APIRouter()

@router.post("/books", status_code=status.HTTP_201_CREATED, response_model=BookDetailModel)
async def create_book(
    book_data: BookCreateModel,  # Schema validates input
    session: Session = Depends(get_session),  # DB dependency
    user_data: dict = Depends(get_current_user)  # Auth dependency
):
    """Create a new book (authenticated users only)"""
    new_book = BookService.create_book(book_data, user_data["user_uid"], session)
    return new_book

@router.get("/books/{book_id}", response_model=BookDetailModel)
async def get_book(
    book_id: str,
    session: Session = Depends(get_session)
):
    """Retrieve a single book by ID"""
    book = BookService.get_book_by_id(book_id, session)
    if not book:
        raise BookNotFound("Book does not exist")
    return book
```

**Responsibilities:**
- ✅ Define HTTP endpoints (GET, POST, PUT, DELETE)
- ✅ Validate input via Pydantic schemas
- ✅ Inject dependencies (DB session, auth)
- ✅ Call service layer methods
- ✅ Return appropriate HTTP status codes
- ❌ NO business logic here
- ❌ NO direct database queries

**What to check in other FastAPI projects:**
- ✅ Are routes thin? (Only HTTP handling, no business logic)
- ✅ Are status codes appropriate? (201 for creation, 204 for deletion)
- ✅ Are dependencies used for auth and DB sessions?
- ✅ Are responses properly typed with `response_model`?

---

#### **Layer 2: `schemas.py` - Data Validation Layer**
**Purpose:** Define contracts for API inputs and outputs

**What it does:**
```python
from pydantic import BaseModel, Field, field_validator, field_serializer
from datetime import date, datetime

class BookCreateModel(BaseModel):
    """Input: Create a book"""
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1)
    publisher: str
    published_date: date
    page_count: int = Field(gt=0)
    language: str = Field(default="English")
    
    @field_validator("published_date")
    def validate_date(cls, v):
        if v > date.today():
            raise ValueError("Published date cannot be in the future")
        return v

class BookDetailModel(BaseModel):
    """Output: Book details"""
    uid: str
    title: str
    author: str
    publisher: str
    published_date: str  # Serialized as string
    page_count: int
    language: str
    created_at: datetime
    
    @field_serializer("published_date")
    def serialize_date(self, value: date) -> str:
        return value.strftime("%Y-%m-%d")
    
    model_config = {"from_attributes": True}  # Allow ORM objects
```

**Key Concepts:**
- **Request vs Response Models:** Separate input and output schemas
- **Validation:** `field_validator` for custom rules
- **Serialization:** `field_serializer` for custom formatting
- **Type Safety:** Pydantic enforces types at runtime
- **from_attributes:** Allows converting SQLModel objects to Pydantic

**What to check in other FastAPI projects:**
- ✅ Are request and response models separate?
- ✅ Are validations comprehensive? (min/max length, ranges, regex)
- ✅ Are dates/datetimes properly serialized?
- ✅ Is `model_config` set for ORM compatibility?

---

#### **Layer 3: `service.py` - Business Logic Layer**
**Purpose:** Core application logic, database operations, business rules

**What it does:**
```python
from sqlmodel import Session, select
from .models import Book
from .schemas import BookCreateModel

class BookService:
    @staticmethod
    def create_book(book_data: BookCreateModel, user_uid: str, session: Session) -> Book:
        """Create a new book entry"""
        # Business logic: Check if user has permission
        # Business logic: Validate publisher exists
        
        new_book = Book(
            **book_data.model_dump(),
            user_uid=user_uid
        )
        
        session.add(new_book)
        session.commit()
        session.refresh(new_book)  # Get DB-generated fields
        
        return new_book
    
    @staticmethod
    def get_book_by_id(book_id: str, session: Session) -> Book | None:
        """Retrieve a book by UUID"""
        statement = select(Book).where(Book.uid == book_id)
        return session.exec(statement).first()
    
    @staticmethod
    def get_all_books(session: Session, skip: int = 0, limit: int = 10) -> list[Book]:
        """Get paginated list of books"""
        statement = select(Book).offset(skip).limit(limit)
        return session.exec(statement).all()
    
    @staticmethod
    def update_book(book_id: str, book_data: dict, session: Session) -> Book:
        """Update book details"""
        book = BookService.get_book_by_id(book_id, session)
        if not book:
            raise BookNotFound("Book does not exist")
        
        for key, value in book_data.items():
            setattr(book, key, value)
        
        book.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(book)
        
        return book
    
    @staticmethod
    def delete_book(book_id: str, session: Session):
        """Delete a book"""
        book = BookService.get_book_by_id(book_id, session)
        if not book:
            raise BookNotFound("Book does not exist")
        
        session.delete(book)
        session.commit()
```

**Responsibilities:**
- ✅ Business logic (validation, permissions, calculations)
- ✅ Database operations (CRUD)
- ✅ Raise domain exceptions
- ✅ Transaction management (commit/rollback)
- ❌ NO HTTP concerns (status codes, headers)
- ❌ NO request/response handling

**What to check in other FastAPI projects:**
- ✅ Is business logic separated from routes?
- ✅ Are services stateless? (No instance variables)
- ✅ Are exceptions raised for error conditions?
- ✅ Are database queries optimized? (No N+1 queries)

---

#### **Auth-Specific Files:**

**`utils.py` - Cryptography & JWT Utilities**
```python
from passlib.context import CryptContext
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain, hashed)

def create_access_token(user_data: dict) -> str:
    """Generate JWT access token"""
    payload = {
        "user_uid": str(user_data["uid"]),
        "email": user_data["email"],
        "role": user_data["role"],
        "exp": datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES),
        "jti": str(uuid.uuid4())  # Unique token ID
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode and validate JWT"""
    try:
        return jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise InvalidToken("Token has expired")
    except jwt.JWTError:
        raise InvalidToken("Invalid token")
```

**`dependencies.py` - Authentication Guards**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> dict:
    """Verify token and return user data"""
    token = credentials.credentials
    
    # Decode token
    payload = decode_token(token)
    
    # Check if token is revoked
    if await is_jti_blocklisted(payload["jti"]):
        raise HTTPException(status_code=401, detail="Token has been revoked")
    
    return payload

async def require_admin(user_data: dict = Depends(get_current_user)):
    """Require admin role"""
    if user_data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_data
```

**What to check in other FastAPI projects:**
- ✅ Is password hashing used? (bcrypt, argon2)
- ✅ Are JWTs properly signed and validated?
- ✅ Is there a token blocklist for logout?
- ✅ Are role-based access controls implemented?
- ✅ Is HTTPBearer security scheme used?

---

### 4️⃣ **Background Processing (Celery)**

#### `src/celery_tasks.py` - Async Task Definitions
**Purpose:** Offload slow operations (email, file processing) to background workers

**What it does:**
```python
from celery import Celery

celery_app = Celery(
    "bookly",
    broker=f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/0",
    backend=f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/1"
)

@celery_app.task(name="send_email")
def send_email_task(recipient: str, subject: str, body: str):
    """Send email in background"""
    from src.mail import send_email
    send_email(recipient, subject, body)

# Usage in routes:
send_email_task.delay("user@example.com", "Welcome", "Thanks for signing up!")
```

**Key Concepts:**
- **Broker:** Redis queues tasks
- **Worker:** Separate process executes tasks
- **Result Backend:** Stores task results
- **Retry Logic:** Auto-retry failed tasks

**What to check in other FastAPI projects:**
- ✅ Is Celery used for long-running tasks?
- ✅ Are tasks idempotent? (Safe to retry)
- ✅ Is there monitoring (Flower)?
- ✅ Are task results stored if needed?

---

#### `src/mail.py` - Email Service
**Purpose:** Send emails via SMTP

**What it does:**
```python
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_PORT=587,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False
)

async def send_email(recipient: str, subject: str, body: str):
    """Send HTML email"""
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        body=body,
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)
```

**What to check in other FastAPI projects:**
- ✅ Is email sending asynchronous?
- ✅ Are templates used for email bodies?
- ✅ Is SMTP configuration secure?

---

### 5️⃣ **Testing (`src/tests/`)**

#### `conftest.py` - Test Fixtures
**Purpose:** Set up test database, client, and fixtures

**What it does:**
```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel

@pytest.fixture
def test_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///./test.db")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def client(test_session):
    """Create a test client with overridden dependencies"""
    def override_get_session():
        yield test_session
    
    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()
```

**What to check in other FastAPI projects:**
- ✅ Are tests using a separate test database?
- ✅ Are dependencies overridden for testing?
- ✅ Is test data cleaned up after tests?

---

## 🔄 Request Flow Diagram

```
1. HTTP Request arrives
        ↓
2. Middleware Stack (Security, Logging, CORS)
        ↓
3. Route Handler (routes.py)
        ↓
4. Schema Validation (Pydantic)
        ↓
5. Dependency Injection (DB Session, Auth)
        ↓
6. Service Layer (Business Logic)
        ↓
7. Database / Redis / External Service
        ↓
8. Response Serialization (Pydantic)
        ↓
9. Middleware Stack (Add headers, log response)
        ↓
10. HTTP Response returned
```

**Error Handling:**
```
Exception raised anywhere
        ↓
Global Exception Handler (errors.py)
        ↓
Logged + Converted to HTTP Response
        ↓
Returned to client
```

---

## 🎯 Key Architectural Patterns Used

### 1. **Clean Architecture**
- **Independence:** Business logic doesn't depend on frameworks
- **Testability:** Each layer can be tested independently
- **Flexibility:** Can swap databases, frameworks without rewriting logic

### 2. **Dependency Injection**
- Routes receive dependencies via `Depends()`
- Makes testing easy (mock dependencies)
- Promotes loose coupling

### 3. **Repository Pattern** (via Services)
- Services abstract database operations
- Controllers don't know about SQL
- Easy to switch ORMs or databases

### 4. **DTO Pattern** (via Pydantic Schemas)
- Data Transfer Objects for input/output
- Validation at API boundary
- Type safety throughout application

### 5. **Middleware Pattern**
- Cross-cutting concerns (logging, auth, CORS)
- Keeps routes clean
- Reusable across applications

---

## ✅ FastAPI Project Checklist

Use this when evaluating any FastAPI project:

### **Architecture**
- [ ] Is the code organized by feature (not by layer)?
- [ ] Is business logic separated from routes?
- [ ] Are services used for database operations?
- [ ] Is dependency injection used properly?

### **Configuration**
- [ ] Is `pydantic-settings` used?
- [ ] Are secrets stored in `.env` (not hardcoded)?
- [ ] Are environment-specific configs available?

### **Database**
- [ ] Is an ORM used (SQLModel/SQLAlchemy)?
- [ ] Are migrations handled (Alembic)?
- [ ] Are relationships properly defined?
- [ ] Is connection pooling configured?
- [ ] Are indexes created on queried columns?

### **Authentication**
- [ ] Is JWT used for stateless auth?
- [ ] Are passwords hashed (bcrypt/argon2)?
- [ ] Is there a token refresh mechanism?
- [ ] Is logout implemented (blocklist)?
- [ ] Are roles/permissions enforced?

### **API Design**
- [ ] Are Pydantic schemas used for validation?
- [ ] Are status codes appropriate?
- [ ] Is pagination implemented?
- [ ] Are errors handled consistently?
- [ ] Is OpenAPI documentation accurate?

### **Security**
- [ ] Is CORS configured?
- [ ] Are security headers set?
- [ ] Is input sanitized?
- [ ] Are SQL injections prevented (ORM)?
- [ ] Is rate limiting implemented?

### **Testing**
- [ ] Are unit tests present?
- [ ] Are integration tests present?
- [ ] Is test coverage >70%?
- [ ] Are dependencies mocked?

### **Performance**
- [ ] Is async/await used where appropriate?
- [ ] Is caching implemented (Redis)?
- [ ] Are background tasks used for slow operations?
- [ ] Are database queries optimized (no N+1)?

### **Deployment**
- [ ] Is Docker used?
- [ ] Is docker-compose configured?
- [ ] Are health check endpoints present?
- [ ] Is logging configured?
- [ ] Are environment variables documented?

---

## 🧠 Mental Model (TL;DR)

```
HTTP Request
    → Middleware (Security, Logging)
    → Route (HTTP Handling)
    → Schema (Validation)
    → Dependency (Auth, DB Session)
    → Service (Business Logic)
    → Database / Redis / External Service
    → Schema (Serialization)
    → Route (HTTP Response)
    → Middleware (Headers, Logging)
HTTP Response
```

**Errors:** Caught globally → Logged → Converted to HTTP response
**Background Tasks:** Offloaded to Celery → Executed asynchronously

This architecture is **scalable**, **testable**, and **maintainable**.