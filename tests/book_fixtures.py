from app.extensions import db
from app.models.user import User
from app.models.book import Cookbook, Magazine


class BookFixtures:
    """Sets up Book Fixtures
    expects 'user_1' and 'user_2' to be present (general app fixtures)
    book_1 - type: cookbook, user: user_1
    book_2 - type: magazine, user: user_1
    book_3 - type: cookbook, user: user_2
    book_4 - type: magazine, user: user_2
    """

    def __init__(self, app):
        self._app = app

        self.user_1 = None
        self.user_2 = None
        self.book_1 = None
        self.book_2 = None
        self.book_3 = None
        self.book_4 = None

        with app.app_context(), app.test_request_context():
            user_1: User = db.session.execute(
                db.select(User).filter_by(username="user_1")
            ).scalar_one()
            self.user_1 = user_1.to_dict()
            user_2: User = db.session.execute(
                db.select(User).filter_by(username="user_2")
            ).scalar_one()
            self.user_2 = user_2.to_dict()

            for i in range(4):
                b_data = {
                    "title": "b_{:d}".format(i + 1),
                    "type": "cookbook" if i % 2 == 0 else "magazine",
                    "year": 2015 + i,
                    "author": "author_{:d}".format(i + 1) if i % 2 == 0 else None,
                    "issue": "{:d}".format(i + 1) if i % 2 != 0 else None,
                }
                if i % 2 == 0:
                    b = Cookbook()
                else:
                    b = Magazine()
                b.from_dict(b_data)
                if i < 2:
                    user_1.books.append(b)
                else:
                    user_2.books.append(b)

                db.session.add(b)
                db.session.commit()
                self.__setattr__("book_{:d}".format(i + 1), b.to_dict())
