import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash, session
from werkzeug.exceptions import abort
import logging
from logging.config import dictConfig
from flask_session import Session



dictConfig(
    {
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(levelname)s:%(module)s:%(asctime)s, %(message)s',
                'datefmt': '%d/%m/%Y, %H:%M:%S',
            }
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': 'app.log',
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['wsgi']
        }
    }
)

MSG_ENDPT_FMT = '%s endpoint was reached'
GOOD_MSG_FMT = 'Article %s retrieved!'
BAD_MSG_FMT = 'Page with wrong index = %s was accessed'
CREATE_MSG_FMT = 'Article %s created'

# Function to get a database connection.
# This function connects to database with the name `database.db`
connectionCount = 0


def get_db_connection():
    global connectionCount
    connectionCount += 1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection



# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    
    return post

def get_title(post_id):
    connection = get_db_connection()
    title = connection.execute('SELECT title FROM posts WHERE id = ?',
                               (post_id,)).fetchone()
    connection.close()

    return title.getValue()

# Define the Flask application



# Define the main route of the web application 
def create_app():
    app = Flask(__name__)
    return app

app = create_app()

# def add_count():
#     connection = get_db_connection()
#     count = connection.execute('SELECT counter FROM count').fetchone()
#     count = count + 1
#     connection.execute('UPDATE count SET counter = (?)',(count))
#     connection.close()

# def get_count():
#     connection = get_db_connection()
#     count = connection.execute('SELECT counter FROM count').fetchone()
#     connection.close()
#     return count.getValue()

@app.route('/')
def index():
    # add_count()
    app.logger.debug(GOOD_MSG_FMT, 'index')
    connection = get_db_connection()
    
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    global connectionCount
    connectionCount += 1
    post = get_post(post_id)
    if post is None:
      app.logger.error(BAD_MSG_FMT, post_id)
      return render_template('404.html'), 404
    else:
      app.logger.info(GOOD_MSG_FMT, post['title'])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    global connectionCount
    connectionCount += 1
    app.logger.info(GOOD_MSG_FMT, 'About page')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info(CREATE_MSG_FMT, title)
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def health():
    try:
        connection = get_db_connection()
        posts = connection.execute('SELECT * FROM posts').fetchall()
        connection.close()
    except:
        return {'result': 'ERROR - unhealthy'}
    global connectionCount
    connectionCount += 1
    return {'result': 'OK - healthy'}

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    noOfPost = len(posts)
    return {'db_connection_count': connectionCount, 'post_count': noOfPost}


# start the application on port 3111

app.run(host='0.0.0.0', port='3111')
