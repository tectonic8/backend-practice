import os
import json
import sqlite3

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

class DB(object):
    """
    DB driver for the Todo app - deals with writing entities
    to the DB and reading entities from the DB
    """

    def __init__(self):
        self.conn = sqlite3.connect("posts.db", check_same_thread=False)
        self.conn = sqlite3.connect("comments.db", check_same_thread=False)
        # TODO - Create all other tables here
        self.delete_tables()
        self.create_posts_table()
        self.create_comments_table()

    def create_posts_table(self):
        #id, score, text, and username
        try:
            self.conn.execute("""
                CREATE TABLE posts
                (ID INTEGER PRIMARY KEY,
                SCORE INT NOT NULL,
                TEXT TEXT NOT NULL,
                USERNAME TEXT NOT NULL);
            """)
        except Exception as e:
            print(e)

    def create_comments_table(self):
        try:
            self.conn.execute("""
                CREATE TABLE comments
                (ID INTEGER PRIMARY KEY,
                PARENT INT NOT NULL,
                SCORE INT NOT NULL,
                TEXT TEXT NOT NULL,
                USERNAME TEXT NOT NULL);
            """)
        except Exception as e:
            print(e)

    def delete_tables(self):
        self.conn.execute("""DROP TABLE IF EXISTS posts;""")
        self.conn.execute("""DROP TABLE IF EXISTS comments;""")

    def get_posts(self):
        cursor = self.conn.execute("""SELECT * FROM posts;""")
        posts = []
        for row in cursor:
            posts.append({
                'id': row[0],
                'score': row[1],
                'text': row[2],
                'username': row[3]
            })
        return posts

    def create_post(self, content, username):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO posts (SCORE, TEXT, USERNAME) VALUES (?,?,?);', (0, content, username))
        self.conn.commit()
        return cursor.lastrowid

    def get_post_by_id(self, id):
        cursor = self.conn.execute('SELECT * FROM posts WHERE id = ?', (id,))
        for row in cursor:
            return {
                'id': row[0],
                'score': row[1],
                'text': row[2],
                'username': row[3]
            }
        return None

    def edit_post_by_id(self, post_id, content):
        self.conn.execute("""
            UPDATE posts
            SET text = ?
            WHERE id = ?;
        """, (content, post_id))
        self.conn.commit()

    def delete_post_by_id(self, post_id):
        self.conn.execute("""
            DELETE FROM posts
            WHERE id = ?;
        """, (post_id,))
        self.conn.commit()

    def get_posts_by_username(self, username):
        cursor = self.conn.execute('SELECT * FROM posts WHERE username = ?', (username,))
        posts = []
        for row in cursor:
            posts.append({
                'id': row[0],
                'score': row[1],
                'text': row[2],
                'username': row[3]
            })
        return posts

    def get_comments(self, post_id):
        cursor = self.conn.execute('SELECT * FROM comments WHERE parent = ?', (post_id,))
        comment_list = []
        for row in cursor:
            comment_list.append({
                'id': row[0],
                'score': row[2],
                'text': row[3],
                'username': row[4]
            })
        return comment_list

    def create_comment(self, post_id, content, username):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO comments (PARENT, SCORE, TEXT, USERNAME) VALUES (?,?,?,?);', (post_id, 0, content, username))
        self.conn.commit()
        return cursor.lastrowid
    


# Only <=1 instance of the DB driver
# exists within the app at all times
DB = singleton(DB)
