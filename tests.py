import microblog
import unittest

class testBlog(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(testBlog, self).__init__(*args, **kwargs)
        microblog.app.config['SQLALCHEMY_DATABASE_URI']='postgres:///blagtest'

    def setUp(self):
        microblog.db.create_all()

    def tearDown(self):
        microblog.db.session.close()
        microblog.db.drop_all()

    def testBlagPost(self):
        microblog.write_post("test title", "test body")
        microblog.write_post("test title2", "test body2")
        microblog.write_post("test title3", "test body3")

        blags = microblog.BlagPost.query.all()

        self.assertEqual(blags[0].title, "test title")
        self.assertEqual(blags[2].body, "test body3")

    def testBlagGet(self):
        microblog.write_post("test title", "test body")
        microblog.write_post("test title2", "test body2")
        microblog.write_post("test title3", "test body3")
        a = microblog.get_posts()

        self.assertEqual(a[0].title, "test title")
        self.assertEqual(a[2].body, "test body3")

    def testSingleGet(self):
        microblog.write_post("test title", "test body")
        microblog.write_post("test title2", "test body2")
        microblog.write_post("test title3", "test body3")

        self.assertEqual(microblog.get_post(1).title, "test title")
        self.assertEqual(microblog.get_post(3).body, "test body3")

if __name__ == "__main__":
    unittest.main()