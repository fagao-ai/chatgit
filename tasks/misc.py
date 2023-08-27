import uvicorn
from invoke import task
from invoke.context import Context


@task
def clean(ctx: Context):
    ctx.run("rm -rf dist/* build/*")
    ctx.run('find . -type d -name "__pycache__" -exec rm -r {} +')


@task(aliases=["s"])
def server(_: Context):
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        log_level="debug",
    )
