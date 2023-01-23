from app import create_app, db
from app.models.user import User
from app.models.role import Role

app = create_app()


@app.shell_context_processor
def make_shell_context():
    query = db.session.execute(
        db.select(User).where(User.username == "admin")
    ).fetchone()

    if query:
        admin: User = query[0]
    else:
        admin = None

    return {"db": db, "admin": admin, "User": User, "Role": Role}
