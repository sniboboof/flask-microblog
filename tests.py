import microblog
import unittest
import os

class testBlog(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(testBlog, self).__init__(*args, **kwargs)
        microblog.app.config['SQLALCHEMY_DATABASE_URI']='postgres://postgres:@localhost/blagtest'
        microblog.app.config['TESTING']=True

    def setUp(self):
        microblog.app.config['TESTING'] = True
        self.app = microblog.app.test_client()
        microblog.db.create_all()

    def tearDown(self):
        microblog.db.session.close()
        microblog.db.drop_all()

    def testRegisterAuthor(self):
        microblog.register_author('jack', 'markley')
        microblog.register_author('ben', 'markley')
        microblog.register_author('jeff', 'david')

        authros = microblog.Author.query.all()

        self.assertEqual(authros[0].name, 'jack')
        self.assertEqual(authros[2].name, 'jeff')
        self.assertEqual(authros[1].password, 'markley')
        self.assertEqual(authros[2].password, 'david')

    def testBlagPost(self):
        microblog.register_author('jack', 'markley')
        microblog.write_post("test title", "test body", 1)
        microblog.write_post("test title2", "test body2", 1)
        microblog.write_post("test title3", "test body3", 1)

        blags = microblog.BlagPost.query.all()

        self.assertEqual(blags[0].title, "test title")
        self.assertEqual(blags[2].body, "test body3")

    def testBlagGet(self):
        microblog.register_author('jack', 'markley')
        microblog.write_post("test title", "test body", 1)
        microblog.write_post("test title2", "test body2", 1)
        microblog.write_post("test title3", "test body3", 1)
        a = microblog.get_posts()

        self.assertEqual(a[2].BlagPost.title, "test title")
        self.assertEqual(a[0].BlagPost.body, "test body3")

    def testSingleGet(self):
        microblog.register_author('jack', 'markley')
        microblog.write_post("test title", "test body", 1)
        microblog.write_post("test title2", "test body2", 1)
        microblog.write_post("test title3", "test body3", 1)

        self.assertEqual(microblog.get_post(1).BlagPost.title, "test title")
        self.assertEqual(microblog.get_post(3).BlagPost.body, "test body3")

    def testPostsView(self):
        microblog.register_author('jack', 'markley')
        microblog.register_author('jeff', 'haskins')
        microblog.register_author('ben', 'markley')
        rv = self.app.get('/')
        assert 'No posts yet' in rv.data

        microblog.write_post("test title", "test body", 1)
        microblog.write_post("test title2", "test body2", 1)
        microblog.write_post("test title3", "test body3", 2)
        rv = self.app.get('/')
        assert 'test title' in rv.data
        assert 'test title2' in rv.data
        assert 'test title3' in rv.data
        assert 'jack' in rv.data
        assert 'jeff' in rv.data
        assert 'ben' not in rv.data

    def testPostView(self):
        microblog.register_author('jack', 'markley')
        microblog.register_author('jeff', 'haskins')
        rv = self.app.get('/post/1')
        assert "That post hasn't been written yet!" in rv.data

        microblog.write_post("test title", "test body", 1)
        microblog.write_post("test title2", "test body2", 2)
        microblog.write_post("test title3", "test body3", 1)
        rv = self.app.get('/post/1')
        assert 'test title' in rv.data
        assert 'test body' in rv.data
        assert 'jack' in rv.data
        assert 'jeff' not in rv.data
        rv = self.app.get('/post/2')
        assert 'test title2' in rv.data
        assert 'test body2' in rv.data
        assert 'jeff' in rv.data
        assert 'jack' not in rv.data
        rv = self.app.get('/post/3')
        assert 'test title3' in rv.data
        assert 'test body3' in rv.data
        assert 'jack' in rv.data
        rv = self.app.get('/post/78')
        assert "That post hasn't been written yet!" in rv.data

    def testLogIn(self):
        rv = self.app.get('/login')
        assert 'Method Not Allowed' in rv.data
        microblog.register_author('jack', 'markley')
        microblog.register_author('jeff', 'haskins')
        rv = self.app.post('login', data={'username':'hurr', 'password':'durr'})
        assert 'Username or password was incorrect' in rv.data
        rv = self.app.post('login', data={'username':'jack', 'password':'durr'})
        assert "Username or password was incorrect" in rv.data
        rv = self.app.post('login', data={'username':'jeff', 'password':'markley'})
        assert "Username or password was incorrect" in rv.data
        rv = self.app.post('login', data={'username':'jack', 'password':'markley'}, follow_redirects=True)
        assert "logged in as jack" in rv.data

    def testLogOut(self):
        microblog.register_author('jack', 'markley')
        microblog.register_author('jeff', 'haskins')
        rv = self.app.get('/logout', follow_redirects=True)
        assert 'Method Not Allowed' in rv.data
        self.app.post('login', {'username':'jack', 'password':'markley'})
        rv=self.app.post('/logout', follow_redirects=True)
        assert 'username:' in rv.data

    def testWriteView(self):
        pass

if __name__ == "__main__":
    unittest.main()