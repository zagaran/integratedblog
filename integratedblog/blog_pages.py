from auth_helpers import clear_logged_in_admin, get_oauth2_flow, \
    logged_in_admin, require_admin_login, try_to_log_in_from_oauth2_callback
from data_models import Author, BlogPost
from flask import Blueprint, redirect, render_template, request, url_for
from playhouse.flask_utils import get_object_or_404

blog_pages = Blueprint("blog_pages", __name__)


# TODO: figure out customizable templates


# List all blog posts, or all blog posts by one author
@blog_pages.route('/', methods=['GET', 'POST'])
def show_all_published_blog_posts():
    author = None
    if 'author' in request.args:
        author = get_object_or_404(Author, Author.name==request.args.get('author'))
    return render_template('blog_post_list.html', author=author,
                           logged_in_admin=logged_in_admin(),
                           blog_post_list=BlogPost.get_blog_post_list(author))


# View a specific blog post
@blog_pages.route('/<slug>', methods=['GET'])
def view_blog_post(slug):
    return render_template('view_blog_post.html',
                           blog_post=BlogPost.get_blog_post_from_slug(slug, logged_in_admin()),
                           logged_in_admin=logged_in_admin())


@blog_pages.route('/admin/new_post', methods=['GET', 'POST'])
@require_admin_login
def new_blog_post():
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('content'):
            new_post = BlogPost.create_new_blog_post(request.form.get('author'),
                                                     request.form.get('title'),
                                                     request.form.get('content'),
                                                     request.form.get('date_published'))
            return redirect(url_for('blog_pages.view_blog_post', slug=new_post.slug))
    return render_template('edit_blog_post.html',
                           authors=Author.select(),
                           logged_in_admin=logged_in_admin())


@blog_pages.route('/admin/edit_post/<slug>', methods=['GET', 'POST'])
@require_admin_login
def edit_blog_post(slug):
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('content'):
            BlogPost.update_blog_post(slug,
                                      request.form.get('author'),
                                      request.form.get('title'),
                                      request.form.get('content'),
                                      request.form.get('date_published'))
        return redirect(url_for('blog_pages.view_blog_post', slug=slug))
    return render_template('edit_blog_post.html', edit=True,
                           authors=Author.select(),
                           blog_post=BlogPost.get_blog_post_from_slug(slug, True),
                           logged_in_admin=logged_in_admin())


@blog_pages.route('/admin/publish/<slug>', methods=['GET'])
@require_admin_login
def publish_blog_post(slug):
    BlogPost.publish_blog_post(slug)
    return redirect(url_for('blog_pages.view_blog_post', slug=slug))


@blog_pages.route('/admin/delete/<slug>', methods=['GET'])
@require_admin_login
def delete_blog_post(slug):
    blog_post = BlogPost.get_blog_post_from_slug(slug, True)
    blog_post.delete_instance()
    return redirect(url_for('blog_pages.show_all_draft_blog_posts'))


@blog_pages.route('/admin/drafts', methods=['GET'])
@require_admin_login
def show_all_draft_blog_posts():
    return render_template('blog_post_list.html', drafts=True,
                           logged_in_admin=logged_in_admin(),
                           blog_post_list=BlogPost.get_blog_post_list(published=False))


@blog_pages.route('/admin/login', methods=['GET'])
def log_in():
    return redirect(get_oauth2_flow().step1_get_authorize_url())


@blog_pages.route('/admin/oauth2callback')
def oauth2callback():
    auth_code = request.args.get("code")
    login_succeeded, email = try_to_log_in_from_oauth2_callback(auth_code)
    if login_succeeded:
        return redirect(url_for('blog_pages.show_all_published_blog_posts'))
    else:
        return "Unauthorized email address " + email


@blog_pages.route('/admin/logout', methods=['GET'])
def log_out():
    clear_logged_in_admin()
    return redirect(url_for('blog_pages.show_all_published_blog_posts'))
