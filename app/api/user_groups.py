from . import bp
from app.api.errors import bad_request
from app.models.user import User
from app.models.user_group import UserGroup
from app.extensions import db
from flask import jsonify, request, url_for, abort
from app.api.auth import token_auth
from app.validators import required_fields

ALREADY_IN_GROUP = "user is already in a group"


@bp.route("/user_groups", methods=["POST"])
@token_auth.login_required()
@required_fields(["group_name"])
def create_new_user_group():
    """Create a new user group and add the current as group admin.
    Users may only be in one group at a time.
    """

    user: User = token_auth.current_user()
    data = request.get_json() or {}

    # User can only create and be in one group
    if user.user_group:
        return bad_request(ALREADY_IN_GROUP)

    group_name = data["group_name"]

    user_group = UserGroup()
    user_group.group_name = group_name
    user_group.group_admin = user

    db.session.add(user_group)
    db.session.commit()

    user.user_group = user_group
    db.session.add(user)
    db.session.commit()

    response = jsonify(user_group.to_dict())
    response.status_code = 201
    response.content_location = url_for("api.get_user_group", id=user_group.id)

    return response

@bp.route("/user_groups/<int:id>", methods=["GET"])
@token_auth.login_required()
def get_user_group(id):
    user: User = token_auth.current_user()

    # query the user group by id and join the users with user id
    stmt = (
        db.select(UserGroup)
        .where(UserGroup.id == id)
        .join(User, User.user_group_id == UserGroup.id)
    )
    user_group = db.session.execute(stmt).scalars().first()

    # return only if user is in the group otherwise 404
    if user_group and user in user_group.users:
        return jsonify(user_group.to_dict())
    else:
        abort(404)


@bp.route("/user_groups/<int:group_id>", methods=["DELETE"])
@token_auth.login_required()
def delete_user_group(group_id):
    user: User = token_auth.current_user()

    # query the user group by id and join the users with user id
    stmt = db.select(UserGroup).where(UserGroup.id == group_id)
    user_group = db.session.execute(stmt).scalars().one_or_none()
    if not user_group:
        abort(404)

    # only group admin may delete group
    if user_group.group_admin_user_id != user.id:
        abort(403)

    db.session.execute(db.delete(UserGroup).where(UserGroup.id == group_id))
    db.session.execute(
        db.update(User).where(User.user_group_id == group_id).values(user_group_id=None)
    )
    db.session.commit()

    return "", 204


@bp.route("/user_groups/<int:group_id>/users", methods=["PUT"])
@token_auth.login_required()
@required_fields(["user_id"])
def add_user_to_group(group_id):
    user: User = token_auth.current_user()
    data = request.get_json() or {}

    # abort if user is self
    if user.id == data["user_id"]:
        return bad_request("cannot add self to group")

    # query the user group by group_id and join the users with user id
    stmt = (
        db.select(UserGroup)
        .where(UserGroup.id == group_id)
        .join(User, User.user_group_id == UserGroup.id)
    )
    user_group = db.session.execute(stmt).scalars().first()

    if not user_group:
        abort(404)

    # abort if user is not group admin
    if user.group_admin_of != user_group:
        abort(403)

    # get user to add
    user_to_add = db.session.execute(
        db.select(User).where(User.id == data["user_id"])
    ).scalar_one_or_none()
    if not user_to_add:
        abort(404)

    # if user is already in any group abort
    if user_to_add.user_group:
        return bad_request(ALREADY_IN_GROUP)

    # if user is not in the group add the user to the group
    if user_group and user_to_add not in user_group.users:
        user_group.users.append(user_to_add)
        db.session.add(user_group)
        db.session.commit()

        return jsonify(user_group.to_dict())
    else:
        return bad_request(ALREADY_IN_GROUP)


# add user to group by email
@bp.route("/user_groups/<int:group_id>/users/email", methods=["PUT"])
@token_auth.login_required()
@required_fields(["email"])
def add_user_to_group_by_email(group_id):
    data = request.get_json() or {}
    # get user_to_add by email
    user_to_add = db.session.execute(
        db.select(User).where(User.email == data["email"])
    ).scalar_one_or_none()

    if not user_to_add:
        abort(404)

    request.json["user_id"] = user_to_add.id
    return add_user_to_group(group_id)


@bp.route("/user_groups/<int:group_id>/users/<int:user_id>", methods=["DELETE"])
@token_auth.login_required()
def delete_user_from_group(group_id, user_id):
    """Remove a user from a group. Only group admin or the user themselves may remove a user from a group.
    The group admin may not remove themselves from the group.
    """

    requesting_user: User = token_auth.current_user()
    user_to_remove: User = db.session.execute(
        db.select(User).where(User.id == user_id)
    ).scalar_one_or_none()

    if not user_to_remove:
        abort(404)

    # query the user group
    user_group = (
        db.session.execute(db.select(UserGroup).where(UserGroup.id == group_id))
        .scalars()
        .one_or_none()
    )

    if not user_group:
        abort(404)

    # users may only remove themselves from a group or be removed by group admin
    is_self = requesting_user.id == user_to_remove.id
    is_group_admin = requesting_user.id == user_group.group_admin_user_id
    if not (is_self or is_group_admin):
        abort(403)
    # group admin may not remove themselves from the group
    if is_group_admin and is_self:
        return bad_request("group admin may not remove themselves from the group")

    user_group.users.remove(user_to_remove)
    db.session.add(user_group)
    db.session.commit()

    return jsonify(user_group.to_dict())
