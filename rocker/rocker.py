import os
import rest
import click
import base64
import subprocess
import ConfigParser


@click.group()
@click.pass_context
def rocker(ctx):
    ctx.obj = {}
    check_docker()
    credentials = get_credentials()
    if credentials:
        ctx.obj['credentials'] = credentials


@click.command()
@click.option('--username', '-u', type=str)
@click.option('--password', '-p', type=str)
@click.option('--host', '-h', type=str)
@click.pass_context
def login(ctx, username, password, host):
    """Login to private docker registry.

    All options are optional as credentiasl can be retrieved from file

    If no configuration file is present and no options is sent,
    each options are required via prompt.
    It is possible for user to save his credentials.

    Arguments:
        ctx (object): the context
        username (str): The username
        password (str): The password
        host (str): The docker registry host

    Raises:
        (click.Abort): If an error occured during login
    """
    if ctx.obj.get('credentials', False):
        username, password, host, persistent = ctx.obj['credentials']
    else:
        if not username:
            username = click.prompt("Username", type=str)
        if not password:
            password = click.prompt("Password", hide_input=True, type=str)
        if not host:
            host = click.prompt("Host", type=str)

    try:
        res = subprocess.check_output(["docker", "login",
                                       "-u", username,
                                       "-p", password,
                                       host])
        click.echo(res)
        if not ctx.obj.get('credentials', False):
            persistent = False
            msg = "Save credentials (rocker won't ask for username/password/"
            msg += "host on next login)?"
            if click.confirm(msg):
                persistent = True
            save_credentials(username, password, host, persistent)
    except subprocess.CalledProcessError:
        raise click.Abort()


@click.command()
@click.pass_context
def logout(ctx):
    """Logout from docker registry.

    If credentials are not persistent, delete file where they are stored

    Arguments:
        ctx (object): The context

    Raises:
        (click.Abort): If an error occured during logout
    """
    _, _, host, persistent = ctx.obj['credentials']
    try:
        res = subprocess.check_output(["docker", "logout", host])
        click.echo(res)
        if not persistent:
            os.remove(os.path.expanduser("~") + "/.rockerconfig")
    except subprocess.CalledProcessError:
        raise click.Abort()


@click.command()
@click.pass_context
def ping(ctx):
    click.echo(ctx.obj)


@click.command()
@click.pass_context
def catalog(ctx):
    """List repositories

    Arguments:
        tx (object): the context
        repo_name (str): A valid repository name

    Raises:
        (click.ClickException) If user is not logged in
        (click.ClickException) If an error occured
    """
    if not ctx.obj.get('credentials', False):
        msg = click.style("You need to login before using this command.",
                          fg="red")
        raise click.ClickException(msg)
    username, password, host, _ = ctx.obj['credentials']
    token = base64.b64encode(username + ":" + password)
    try:
        repo = rest.get_catalog(host, token)
        if repo:
            click.echo("\n".join(repo))
        else:
            click.echo("No repositories")
    except Exception as e:
        raise click.ClickException(click.style(str(e), fg="red"))


@click.command()
@click.argument("repo_name")
@click.pass_context
def tags(ctx, repo_name):
    """List tag for the given repository

    Arguments:
        ctx (object): the context
        repo_name (str): A valid repository name

    Raises:
        (click.ClickException) If user is not logged in
        (click.ClickException) If an error occured
    """
    if not ctx.obj.get('credentials', False):
        msg = click.style("You need to login before using this command.",
                          fg="red")
        raise click.ClickException(msg)

    username, password, host, _ = ctx.obj['credentials']
    token = base64.b64encode(username + ":" + password)
    try:
        tags = rest.get_tags_list(host, token, repo_name)
        if tags:
            click.echo("\n".join(tags))
        else:
            click.echo("No tags")
    except Exception as e:
        raise click.ClickException(click.style(str(e), fg="red"))


@click.command()
@click.argument("image_name")
@click.pass_context
def delete(ctx, image_name):
    """Delete image

    Arguments:
        ctx (object): the context
        image_name (str): THe image to delete (repo_name:tag)

    Raises:
        (click.ClickException) If user is not logged in
        (click.ClickException) If delete is bnot successful
    """
    if not ctx.obj.get('credentials', False):
        msg = click.style("You need to login before using this command.",
                          fg="red")
        raise click.ClickException(msg)

    username, password, host, _ = ctx.obj['credentials']
    token = base64.b64encode(username + ":" + password)
    repo_name, tag = image_name.split(":")
    try:
        rest.delete_image(host, token, repo_name, tag)
        click.echo("{} succesfully deleted.".format(image_name))
    except Exception as e:
        raise click.ClickException(click.style(str(e), fg="red"))


def check_docker():
    """Check if docker is installed

    Raises:
        (click.ClickException): If docker is not installed
    """
    try:
        subprocess.check_output(["which", "docker"])
    except subprocess.CalledProcessError:
        msg = click.style("rocker requires docker to be installed.",
                          fg="red", bold=True)
        raise click.ClickException(msg)


def get_credentials():
    """Retrieves credentials from file

        Returns:
            (tuple): A tuple made of:
                ::
                    (
                        username,
                        password,
                        host,
                        persistent
                    )
    """
    cfg_filename = os.path.expanduser("~") + "/.rockerconfig"
    if not os.path.exists(cfg_filename):
        return ()
    config = ConfigParser.SafeConfigParser()
    config.read(cfg_filename)
    username = config.get('credentials', 'username')
    password = config.get('credentials', 'password')
    host = config.get('credentials', 'host')
    persistent = config.getboolean('credentials', 'persistent')
    return(username, password, host, persistent)


def save_credentials(username, password, host, persistent=False):
    """Save credentials in file

    Arguments:
        username (str): The username
        password (str): The password
        host (str): The docker registry host

    Keyword Arguments:
        persistent (bool): If credentials should be kept after logout
    """
    with open(os.path.expanduser("~") + "/.rockerconfig", "w") as cfg_file:
        config = ConfigParser.SafeConfigParser()
        config.add_section("credentials")
        config.set("credentials", "host", host)
        config.set("credentials", "username", username)
        config.set("credentials", "password", password)
        # config.set("credentials", "token",
        #            base64.b64encode(username + ":" + password))
        config.set("credentials", "persistent", str(persistent))
        config.write(cfg_file)


# define commands
rocker.add_command(login)
rocker.add_command(logout)
rocker.add_command(ping)
rocker.add_command(catalog)
rocker.add_command(tags)
rocker.add_command(delete)
