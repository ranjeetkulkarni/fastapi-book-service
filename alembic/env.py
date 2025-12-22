import sys
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# --- 1. SETUP PATH TO SRC ---
# This resolves to the project root so we can find 'src'
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

# --- 2. IMPORTS ---
from config import Config
from sqlmodel import SQLModel

# IMPORTANT: Import ALL models here. 
# This executes the class definitions and registers them with SQLModel.metadata.
# Since we merged them, they are all in db.models.
from db.models import Book, User, Review 

# --- 3. ALEMBIC CONFIG ---
config = context.config

# Overwrite the alembic.ini placeholder with your real URL from .env
config.set_main_option("sqlalchemy.url", Config.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This metadata now contains User, Book, AND Review because of the imports above
target_metadata = SQLModel.metadata

# --- STANDARD ALEMBIC BOILERPLATE BELOW (No changes needed) ---
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()