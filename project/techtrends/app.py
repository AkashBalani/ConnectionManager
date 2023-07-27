import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
from logging.config import dictConfig



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
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    app.logger.debug(GOOD_MSG_FMT, 'index')
    global connectionCount
    connection = get_db_connection()
    connectionCount += 1
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
    app.logger.info(GOOD_MSG_FMT, 'About page')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    global connectionCount
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connectionCount += 1
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
    global connectionCount
    connectionCount += 1
    return {'result': 'OK - healthy'}

@app.route('/metrics')
def metrics():
    global connectionCount
    connectionCount += 1
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    noOfPost = len(posts)
    return {'db_connection_count': connectionCount, 'post_count': noOfPost}



# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
