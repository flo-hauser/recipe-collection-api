from app.models.user import User


def filter_by_user_and_group(query, user):
    """Return a query that joins User and filters by user and user_group."""

    return query.join(User).where(
        (User.id == user.id)
        | ((User.user_group_id == user.user_group_id) & (User.user_group_id != None))
    )


def filter_by_user(query, user):
    """Return a query that filters by user."""

    return query.where(User.id == user.id)
