from app import app, db
from app.models import User, ScriptType, JupyterNotebook, PapermillRun


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "JupyterNotebook": JupyterNotebook,
        "PapermillRun": PapermillRun,
        "ScriptType": ScriptType,
    }

