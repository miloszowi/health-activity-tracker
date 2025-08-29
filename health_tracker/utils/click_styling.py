import click

def info(msg: str):
    click.secho(msg, fg="cyan")

def success(msg: str):
    click.secho(msg, fg="green", bold=True)

def warn(msg: str):
    click.secho(msg, fg="yellow")

def error(msg: str):
    click.secho(msg, fg="red", bold=True, err=True)

def step(msg: str):
    click.secho(msg, fg="blue")