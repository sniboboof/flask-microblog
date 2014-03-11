import microblog
import unittest

class testBlog(unittest.TestCase):

    def setUp(self):
        #intiialize a dummy database for the tests to use
        pass

    def tearDown(self):
        #remove the dummy database
        pass

    def testBlagPost(self):
        #test making a post to the blog
        pass

    def testBlagGet(self):
        #test reading the blog posts
        pass

    def testSingleGet(self):
        #test reading a single, complete blog post
        pass

if __name__ == "__main__":
    unittest.main()