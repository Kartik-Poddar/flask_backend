import sqlite3
import time
conn = sqlite3.connect('database.sqlite')
cur = conn.cursor()
# sql_query='''
#         CREATE TABLE USER2( 
#             AUTHOR_ID INTEGER PRIMARY KEY, 
#             USERNAME TEXT NOT NULL UNIQUE, 
#             EMAIL TEXT NOT NULL UNIQUE,
#             PASSWORD TEXT NOT NULL,
#             IMAGE TEXT
#             )
# '''
# cur.execute(sql_query)
# time.sleep(5)
# sql_query='''
#         CREATE TABLE BLOG2( 
#             BLOG_ID INTEGER PRIMARY KEY, 
#             TITLE TEXT NOT NULL, 
#             DATE TEXT NOT NULL,
#             CONTENT TEXT NOT NULL,
#             BLOG_AUTHOR_ID INTEGER,
#             FOREIGN KEY (BLOG_AUTHOR_ID) REFERENCES USER(AUTHOR_ID)
#             )
# '''
# cur.execute(sql_query)
cur.execute('ALTER TABLE USER2 DROP COLUMN IMAGE')

cur.execute('ALTER TABLE USER2 ADD COLUMN IMAGE TEXT NOT NULL DEFAULT "https://img.icons8.com/nolan/64/user.png"')
conn.close()