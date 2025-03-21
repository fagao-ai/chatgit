from invoke import task
from invoke.context import Context


@task
def revision(ctx: Context, comments: str):
    comments = "_".join(comments.split(" "))
    if comments:
        ctx.run(
            f'alembic -c migrations/alembic.ini revision -m "{comments}" --rev-id "`date +%Y%m%d_%H%M%S`" '
        )  # noqa: E501
    else:
        print("Please press migration comments.")


@task
def migrate(ctx: Context):
    command = "upgrade head"
    ctx.run(f"alembic -c migrations/alembic.ini {command}")


@task
def downgrade(ctx: Context, vision: str = "-1"):
    command = f"downgrade {vision}"
    ctx.run(f"alembic -c migrations/alembic.ini {command}")
