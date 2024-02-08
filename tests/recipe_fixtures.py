from app.extensions import db
from app.models.recipe import Recipe
from app.models.user import User
from app.models.book import Book, Cookbook, Magazine
from app.models.tag import Tag


class RecipeFixtures:
    """Sets ip Recipe Fixtures
    depends on user_1, user_2 from app fixtures and BookFixtures
    """

    def __init__(self, app):
        self._app = app

        with app.app_context(), app.test_request_context():
            user_1: User = db.session.execute(
                db.select(User).filter_by(username="user_1")
            ).scalar_one()
            self.user_1 = user_1.to_dict()
            user_2: User = db.session.execute(
                db.select(User).filter_by(username="user_2")
            ).scalar_one()
            self.user_2 = user_2.to_dict()

            book_1: Cookbook = db.session.execute(
                db.select(Book).filter_by(title="b_1")
            ).scalar_one()
            self.book_1 = book_1.to_dict()
            book_2: Magazine = db.session.execute(
                db.select(Book).filter_by(title="b_2")
            ).scalar_one()
            self.book_2 = book_2.to_dict()
            book_3: Cookbook = db.session.execute(
                db.select(Book).filter_by(title="b_3")
            ).scalar_one()
            self.book_3 = book_3.to_dict()

            r_1 = Recipe()
            r_1.book = book_1
            r_1.user = user_1
            r_1.title = "Title - 1"
            r_1.page = 42
            r_1.image_path = "/some/uri"
            r_1.tags = [Tag(tag_name="tag1"), Tag(tag_name="tag2")]

            r_2 = Recipe()
            r_2.book = book_1
            r_2.user = user_1
            r_2.title = "Title - 2"
            r_2.page = 51
            r_2.image_path = "/some/uri/to/another/img"
            r_2.tags = [Tag(tag_name="tag3"), Tag(tag_name="tag4")]

            r_3 = Recipe()
            r_3.book = book_2
            r_3.user = user_1
            r_3.title = "Title - 3"
            r_3.page = 4
            r_3.image_path = "/some/uri/457"
            r_3.tags = [Tag(tag_name="tag5"), Tag(tag_name="tag6")]

            r_3_1 = Recipe()
            r_3_1.book = book_2
            r_3_1.user = user_1
            r_3_1.title = "ein rezept titel"
            r_3_1.page = 4
            r_3_1.image_path = "/some/uri/457"
            r_3_1.tags = [Tag(tag_name="tag7"), Tag(tag_name="tag8")]

            r_3_2 = Recipe()
            r_3_2.book = book_2
            r_3_2.user = user_1
            r_3_2.title = "noch ein rezept"
            r_3_2.page = 4
            r_3_2.image_path = "/some/uri/457"
            r_3_2.tags = [Tag(tag_name="tag9"), Tag(tag_name="tag10")]

            r_4 = Recipe()
            r_4.book = book_3
            r_4.user = user_2
            r_4.title = "Title - 4 another user"
            r_4.page = 4
            r_4.image_path = "/some/uri/4571"

            db.session.add(r_1)
            db.session.add(r_2)
            db.session.add(r_3)
            db.session.add(r_3_1)
            db.session.add(r_3_2)
            db.session.add(r_4)
            db.session.commit()

            self.recipe_1 = r_1.to_dict()
            self.recipe_2 = r_2.to_dict()
            self.recipe_3 = r_3.to_dict()
            self.recipe_3_1 = r_3_1.to_dict()
            self.recipe_3_2 = r_3_2.to_dict()
            self.recipe_4 = r_4.to_dict()
