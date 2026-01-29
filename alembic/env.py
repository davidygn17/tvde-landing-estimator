from logging.config import fileConfig  
from alembic import context
from sqlalchemy import engine_from_config, pool

# Importa as configurações e os modelos
from tvde_qr.settings import settings
from tvde_qr.db import Base
from tvde_qr import models  

# Objeto de configuração do Alembic
config = context.config

# Configura o logging do Python se o arquivo .ini existir
if config.config_file_name is not None:
    fileConfig(config.config_file_name)  # Agora a função existe no código

# Define os metadados para o autogenerate funcionar
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Executa migrações em modo 'offline'."""
    url = settings.database_url  # Usa diretamente a URL do seu .env
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Executa migrações em modo 'online'."""
    configuration = config.get_section(config.config_ini_section) or {}
    
    # FORÇA o Alembic a usar o banco definido no seu arquivo .env
    configuration["sqlalchemy.url"] = settings.database_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
