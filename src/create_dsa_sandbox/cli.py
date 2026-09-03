import typer

from .create_dsa_sandbox import create_dsa_sandbox

app = typer.Typer()
_ = app.command()(create_dsa_sandbox)

if __name__ == "__main__":
    app()
