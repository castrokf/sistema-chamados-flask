from alembic import context

from database import obter_engine


target_metadata = None


def run_migrations_online():
    connectable = obter_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
