import click


@click.group()
@click.option('--userpass', '-u', type=str)
@click.pass_context
def rocker(ctx, userpass):
    ctx.obj = {}
    ctx.obj['login'] = userpass.split(':')[0]
    ctx.obj['pass'] = userpass.split(':')[1]


@click.command()
@click.pass_context
def login(ctx):
    click.echo(ctx.obj)
    click.echo('Login')


@click.command()
@click.pass_context
def ping(ctx):
    click.echo(ctx.obj)


rocker.add_command(login)
rocker.add_command(ping)
