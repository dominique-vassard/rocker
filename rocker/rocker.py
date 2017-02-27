import click
import subprocess


@click.group()
@click.pass_context
def rocker(ctx):
    check_docker()
    ctx.obj = {}


@click.command()
@click.option('--username', '-u', prompt=True, type=str)
@click.option('--password', '-p', prompt=True, hide_input=True, type=str)
@click.argument('url')
@click.pass_context
def login(ctx, username, password, url):
    try:
        res = subprocess.check_output(["docker", "login",
                                       "-u", username,
                                       "-p", password,
                                       url])
        click.echo(res)
    except subprocess.CalledProcessError:
        raise click.Abort


@click.command()
@click.pass_context
def ping(ctx):
    click.echo(ctx.obj)


def check_docker():
    """Check if docker is installed

    Raises:
        (click.ClickException): If docker is not installed
    """
    try:
        subprocess.check_output(["which", "dockr"])
    except subprocess.CalledProcessError:
        msg = click.style("rocker requires docker to be installed.",
                          fg="red", bold=True)
        raise click.ClickException(msg)


rocker.add_command(login)
rocker.add_command(ping)
