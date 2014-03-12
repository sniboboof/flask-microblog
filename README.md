microblog flask app

currently has 3 functions

As a user, when I want to write a post to the blog, I call write_post(title, body) with the post's title in the first argument (no more than 128 characters) and its body in the second argument, so flask will put its entry into the blog database.

As a user, when I want to look at all my blog posts, I call get_posts() so flask will return all the entries in the post table

As a user, when I want to look at a specific blog post, I call get_post(id) with the id primary key of the post so flask will return the only post with that id

travis token: UEnXtp8Txs23Du1sCKvs