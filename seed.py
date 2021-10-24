from models import User, Post, Tag, PostTag, db
from app import app

# Create all tables
db.drop_all()
db.create_all()

phil = User(
    first_name='Dr.',
    last_name='Phil',
)

firstPost = Post(
    title='MY NEW BOOK! Becoming a Phil',
    comment='Just buy the book. I need money',
    posted_by=1,
)

moneyTag = Tag(
    name='#selfImprove'
)

moneyPost = PostTag(
    post_id=1,
    tag_id=1
)

db.session.add(phil)
db.session.commit()
db.session.add(firstPost)
db.session.commit()
db.session.add(moneyTag)
db.session.commit()
db.session.add(moneyPost)
db.session.commit()