import click


@click.command("hello", short_help="Says hello so many times.")
@click.option('-c', '--count', default=1, help='Number of greetings')
@click.option('--title', help="Title to be used")
@click.option('--mr', is_flag=True, default=False, help="Shortcut for --title Mr.")
@click.argument('name', default="World")
def cli(count, title, mr, name):
    """Says hello."""
    if mr:
        title = "Mr."
    if title:
        name = title + " " + name
    for x in range(count):
        click.echo(f"Hello {name}!")
