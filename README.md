# integratedblog
Easy blog add-on for Python Flask web apps.  Most blogs are designed to work as standalone applications; this blog engine is something you can super easily add to an existing Python Flask web app, so that your blog will have the same styling as the rest of your app.

## Features

* Runs on a single-file SQLite database

* Blog administrators log in with their Gmail accounts

* You write blog posts in Markdown, and code blocks have syntax highlighting

## Setup

1. **Install using pip**: `pip install integratedblog`  (Note: this is not yet publicly on pip; you need to clone this repo, `cd` into it, and run `python setup.py install`)

2. **Set up a Google OAuth client for logging in to your blog**: Go to the Google APIs _API Manager_ -> _Credentials_ (https://console.developers.google.com/apis/credentials).  Click _Create Credentials_ -> _OAuth client ID_ -> _Web application_.

    1. Grab the Client ID and Client Secret- you'll use them in Step 3
  
    2. Fill in _Authorized Redirect URIs_ with your website's URL, and with any URLs you'll use for development and testing.  For example, `http://example.com/blog/admin/oauth2callback` and `http://localhost:5000/blog/admin/oauth2callback`.  Replace the word `blog` in `/blog/admin/oauth2callback` with whatever you want the URL extension of your blog to be: for example, `/my_awesome_blog/admin/oauth2callback`.  See in Step 3 how to customize the URL extension.

3. **Add configuration steps to your `app.py` file**:

    ```
    from integratedblog.blog_pages import blog_pages
    from integratedblog.data_models import set_up_blog_db
    ...
    # Anywhere after you've defined "app":
    app.config['BLOG_DATA'] = {
        'authorized_emails': set(["example@gmail.com", "example@example.com"]),  # Blog administrators with these Gmail addresses can log in
        'oauth_client_id': GOOGLE_OAUTH_CLIENT_ID,                               # Get this from step 2
        'oauth_client_secret': GOOGLE_OAUTH_CLIENT_SECRET                        # Get this from step 2
    }
    set_up_blog_db('blog.db')                                                    # Set the filepath for your SQLite database file
    app.register_blueprint(blog_pages, url_prefix="/blog")                       # url_prefix is the URL extension for your blog
    ```

4. **Add template files for the blog pages**

5. **Create authors**: open an `ipython` terminal, and in it, do the following:

   ```
   In [1]: from integratedblog.data_models import Author, set_up_blog_db
   In [2]: set_up_blog_db('/filepath/of/database.db')
   In [3]: Author.create(name="Washington Irving")  # Do this for every Author you want to create
   ```

6. **You're ready to blog!** Log in by going to `example.com/blog/admin/login`, click "Create new blog post", and check that the list of authors you created has correctly populated the dropdown.
