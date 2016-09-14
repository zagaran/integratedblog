from BeautifulSoup import BeautifulSoup
from datetime import datetime
from dateutil.parser import parse
from flask import abort, Markup
from markdown2 import markdown
from peewee import BooleanField, CharField, DateField, DoesNotExist, \
    ForeignKeyField, Model, SqliteDatabase, TextField
import re


db = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db


class Author(BaseModel):
    name = CharField(unique=True)


class BlogPost(BaseModel):
    author = ForeignKeyField(Author, related_name='blogposts')
    title = CharField()
    slug = CharField(unique=True)
    content = TextField()
    date_published = DateField(default=datetime.now())
    published = BooleanField(default=False)
    
    @classmethod
    def create_new_blog_post(cls, author, title, content, date_published):
        return cls.create(author=Author.get(Author.name==author),
                          title=title,
                          slug=generate_url_slug(title),
                          content=content,
                          date_published=parse_date(date_published))
    
    #TODO: add ability to update the url_slug and save a table of 301 redirects from old slugs
    @classmethod
    def update_blog_post(cls, slug, author, title, content, date_published):
        author = Author.get(Author.name == author)
        cls.update(author = author,
                    title = title,
                    content = content,
                    date_published = parse_date(date_published)).where(BlogPost.slug == slug).execute()
    
    @classmethod
    def get_blog_post_from_slug(cls, slug, is_logged_in=False):
        try:
            if is_logged_in:
                return cls.get(BlogPost.slug == slug)
            else:
                return cls.get(BlogPost.slug == slug, BlogPost.published == True)
        except DoesNotExist:
            abort(404)
    
    @classmethod
    def get_blog_post_list(cls, author=None, published=True):
        if author:
            query = cls.select().where(BlogPost.published==published,
                                       BlogPost.author==author)
        else:
            query = cls.select().where(BlogPost.published==published)
        return query.order_by(BlogPost.date_published.desc())
    
    @classmethod
    def publish_blog_post(cls, slug):
        cls.update(published = True).where(BlogPost.slug == slug).execute()
    
    @property
    def html_content(self):
        markdown_filters = ["footnotes",
                            "fenced-code-blocks",
                            "header-ids",
                            "smarty-pants",
                            "tables",
                            "wiki-tables"]
        return Markup(markdown(self.content, extras=markdown_filters))
    
    """ Give a plain-text preview of the content, not more than 100 characters,
    ending with a complete word and an ellipsis """
    @property
    def content_preview(self):
        first_100_chars = un_format(self.content[:400])[:100]
        position_of_last_space = first_100_chars.rfind(' ')
        return first_100_chars[:position_of_last_space] + "..."


def set_up_blog_db(sqlite_database_filepath):
    # db.init() is documented here:
    # http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.init
    db.init(sqlite_database_filepath)
    db.create_tables([Author, BlogPost], safe=True)


def generate_url_slug(blog_post_title):
    return re.sub('[^\w]+', '-', blog_post_title.lower()).strip('-')
 
 
def parse_date(date_string):
    try:
        return parse(date_string)
    except ValueError:
        return datetime.now()


def un_format(raw_content):
    return ''.join(BeautifulSoup(markdown(raw_content)).findAll(text=True))
