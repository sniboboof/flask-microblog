import microblog

microblog.db.create_all()
microblog.db.session.commit()
microblog.register_author("jack", "markley")
microblog.register_author("cris", "ewing")