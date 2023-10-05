from flask import Flask, url_for, jsonify, request
from flask_bcrypt import Bcrypt
import sqlite3
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import os
from PIL import Image
import secrets
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from email.message import EmailMessage
import ssl
import smtplib
from email.mime.text import MIMEText
import re

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'd135449b339f40221a6ba84ff8b5c21f'
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, username, email, password, image):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.image = image
        self.authenticated = False

    def is_active(self):
        return self.is_active()

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    @staticmethod
    def get_reset_token(user_id, expires_sec=120):
        s = Serializer('d135449b339f40221a6ba84ff8b5c21f',expires_sec)
        return s.dumps({'user_id': user_id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        conn = connection()
        cur = conn.cursor()
        s = Serializer('d135449b339f40221a6ba84ff8b5c21f')
        try:
            user_id = s.loads(token)['user_id']
            if user_id is None:
                return None
            user = cur.execute('SELECT * FROM USER2 WHERE AUTHOR_ID=(?)',[user_id])
            user = cur.fetchone()
            return user
            # conn.close()
        except:
            return None
       


@login_manager.user_loader
def load_user(user_id):
    conn = connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM USER2 WHERE AUTHOR_ID=(?)', [user_id])
    user = cur.fetchone()
    if user is None:
        return None
    else:
        return User(int(user[0]), user[1], user[2], user[3], user[4])



def connection():
    conn = None
    try:
        conn = sqlite3.connect('database.sqlite')
    except sqlite3.Error as e:
        print('Error : '+e)

    return conn


@app.route('/')
@app.route('/home',methods=['GET'])
def home():
    conn = connection()
    cur = conn.cursor()
    if request.method == 'GET':
        cur.execute('SELECT BLOG2.BLOG_ID,BLOG2.TITLE,BLOG2.CONTENT,BLOG2.DATE,USER2.USERNAME,USER2.IMAGE FROM BLOG2,USER2 WHERE BLOG2.BLOG_AUTHOR_ID=USER2.AUTHOR_ID ORDER BY BLOG2.DATE DESC')
        posts = [
            dict(id=row[0], author=row[4], title=row[1], date=row[3], content=row[2], image=url_for(
                'static', filename='profile_pics/'+row[5]))
            for row in cur.fetchall()
        ]
        if posts is not None:
            return jsonify(posts)
        else:
            return 'No post'


@app.route('/register', methods=['GET', 'POST'])
def register():
    request_data = request.get_json()
    if current_user.is_authenticated:
        return 'login succesfull via register'
    if request_data:
        new_user = str(request_data['username']).lower()
        new_email = str(request_data['email']).lower()
        new_password = str(request_data['password'])
        confirm_pwd = str(request_data['cfm_pwd'])
        if check_email(new_email) and check_password(new_password) and check_username(new_user) and new_password==confirm_pwd:
            conn = connection()
            cur = conn.cursor()
            image = url_for('static', filename='profile_pics/user')
            hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')
            sql_query = '''
            INSERT INTO USER2(USERNAME,EMAIL,PASSWORD,IMAGE) VALUES (?,?,?,?)
            '''
            cur.execute(sql_query, (new_user, new_email, hashed_pw, image))
            conn.commit()
            conn.close()
            return 'Successful register'
        else:
            return 'Invalid register credentials'
    else:
        return 'Invalid register'
    return 'None'
    

def check_username(username):
    if len(username)<3 or len(username)>20:
        print('length should be between 8 to 20')
        return False
    elif username.isdigit():
        print('username cant be only digits')
        return False
    elif username==None:
        print('cant be none')
        return False
    elif not validate_username(username):
        print('username already exists')
        return False
    return True

def check_email(email):
    if not re.search("^.*@.*\..*$",email):
        print('invalid email')
        return False
    elif email.isdigit():
        print('invalid email cant be only numbers')
        return False
    elif email==None:
        print('email cant be none')
        return False
    elif not validate_email(email):
        print('email already exists')
        return False
    return True

def check_password(pwd):
    if len(pwd)<8:
        print('length cannot be less than 8')
        return False
    elif  pwd==None:
        print('cant be none')
        return False
    elif pwd.isupper():
        print('use both upper and lower case')
        return False
    elif pwd.islower():
        print('use both upper and lower case')
        return False
    return True

def validate_username(username):
        conn = connection()
        cur = conn.cursor()
        sql_query = 'SELECT USERNAME FROM USER2 WHERE USERNAME=?'
        cur.execute(sql_query, (username,))
        user = cur.fetchone()
        conn.close()
        if user:
            return False
        return True

def validate_email(email):
    conn = connection()
    cur = conn.cursor()
    sql_query = 'SELECT EMAIL FROM USER2 WHERE EMAIL=?'
    cur.execute(sql_query, (email,))
    user = cur.fetchone()
    if user:
        return False
    return True

@app.route('/login', methods=['POST'])
def login():
    request_data = request.get_json()
    if current_user.is_authenticated:
        return 'login successfull 1'
    if request_data:
        email = str(request_data['email']).lower()
        password = request_data['password']
        if not validate_email(email) and check_user_password(email,password):
            conn = connection()
            cur = conn.cursor()
            sql_query = 'SELECT * FROM USER2 WHERE EMAIL=?'
            cur.execute(sql_query, (email,))
            temp = cur.fetchone()
            user=User(temp[0],temp[1],temp[2],temp[3],temp[4])
            login_user(user)
            return 'login succesfull 2' 
        else:
            return 'invalid creds'

def check_user_password(email,password):
    conn = connection()
    cur = conn.cursor()
    sql_query = 'SELECT PASSWORD FROM USER2 WHERE EMAIL=?'
    cur.execute(sql_query, (email,))
    user_pwd = cur.fetchone()[0]
    if bcrypt.check_password_hash(user_pwd.encode('utf-8'), password):
        return True
    return False

@app.route('/logout')
def logout():
    logout_user()
    return 'logout successfull'


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex+f_ext
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/account', methods=['GET', 'POST','DELETE'])
@login_required
def account():

    conn = connection()
    cur = conn.cursor()
    
    if request.method == 'DELETE':
        try:
            cur.execute('DELETE FROM USER2 WHERE AUTHOR_ID=(?)', [current_user.id])
            conn.commit()
            cur.execute('DELETE FROM BLOG2 WHERE BLOG_AUTHOR_ID=(?)', [current_user.id])
            conn.commit()
            logout_user()
            return 'Account deleted successfully'
        except Exception as e:
            # Log any errors
            print(f"Error deleting account: {str(e)}")
            return 'An error occurred while deleting the account', 500

    if request.method == 'GET':
        user = current_user.username
        email = current_user.email
        id = current_user.id
        image = url_for(
            'static', filename='profile_pics/'+current_user.image)
        user = {'id':id,'username':user,'email':email,'image':image}
        return jsonify(user)

    if request.method == 'POST':
        try:
            request_data = request.get_json()
            if request_data:
                try:
                    if request_data['image']:
                        # picture_file = save_picture(request_data['image'])
                        current_user.image = request_data['image']
                        cur.execute('UPDATE USER2 SET IMAGE=(?) WHERE USERNAME=(?)', [
                                    current_user.image, current_user.username])
                        conn.commit()
                except:
                    pass
                try:
                    if current_user.username != str(request_data['username']):
                        cur.execute('UPDATE USER2 SET USERNAME=(?) WHERE USERNAME=(?)', [
                                    str(request_data['username']), current_user.username])
                        conn.commit()
                except:
                    pass
                try:
                    if current_user.email != str(request_data['email']):
                        cur.execute('UPDATE USER2 SET EMAIL=(?) WHERE EMAIL=(?)', [
                                    str(request_data['email']), current_user.email])
                        conn.commit()
                except:
                    pass

                return 'updated'     
        except:
            return 'Invalid'
    return 'None'

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    try:
        conn = connection()
        cur = conn.cursor()
        request_data = request.get_json()
        if request_data:
            if request.method=='POST':
                new_title = str(request_data['title']).strip()
                new_content = str(request_data['content']).strip()
                author_id = current_user.id
                now = datetime.now()
                date = now.strftime("%d/%m/%Y %H:%M:%S")
                sql_query = '''
                INSERT INTO BLOG2(TITLE,DATE,CONTENT,BLOG_AUTHOR_ID) VALUES (?,?,?,?)
                '''
                cur.execute(sql_query, (new_title, date, new_content, author_id))
                conn.commit()
                conn.close()
                return 'Your post has been created successfully'
            if request.method=='GET':
                return 'Not allowed'
    except:
        return 'Invalid'
    return None


@app.route('/post/<post_id>', methods=['GET', 'POST','DELETE'])
@login_required
def posts(post_id):
    try:
        conn = connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT BLOG2.BLOG_ID,BLOG2.TITLE,BLOG2.CONTENT,BLOG2.DATE,USER2.USERNAME,USER2.IMAGE,USER2.AUTHOR_ID FROM BLOG2,USER2 WHERE BLOG2.BLOG_AUTHOR_ID=USER2.AUTHOR_ID AND BLOG_ID=(?)', [post_id])
        temp = cur.fetchone()
        post = dict(id=temp[0], author=temp[4], title=temp[1], date=temp[3], content=temp[2], image=url_for(
            'static', filename='profile_pics/'+temp[5]), author_id=temp[6])

        if request.method == 'DELETE':
            if current_user.id==post['author_id']:
                cur.execute('DELETE FROM BLOG2 WHERE BLOG_ID=(?) AND BLOG_AUTHOR_ID=(?)', [post_id,current_user.id])
                conn.commit()
                return 'Post has been successfully deleted'
            else:
                return 'Not Allowed'
        
        if request.method=='GET':
            return jsonify(post)
        
        
        if request.method == 'POST':
            if current_user.id==post['author_id']:
                request_data = request.get_json()
                if request_data:
                    now = datetime.now()
                    date = now.strftime("%d/%m/%Y %H:%M:%S")
                    updated_title = str(request_data['title']).strip()
                    updated_content = str(request_data['content']).strip()
                    cur.execute('UPDATE BLOG2 SET TITLE=(?),DATE=(?),CONTENT=(?) WHERE BLOG_ID=(?) AND BLOG_AUTHOR_ID=(?)', [
                                updated_title, date, updated_content, post_id,current_user.id])
                    conn.commit()
                    return 'Post has been successfully updated'
            else:
                return 'Not Allowed'
    except:
        return 'Invalid'
    
    return 'None'


@app.route('/myBlogs', methods=['GET'])
@login_required
def my_blog():
    if request.method == 'GET':
        conn = connection()
        cur = conn.cursor()
        cur.execute('SELECT BLOG_ID,BLOG2.TITLE,BLOG2.CONTENT,BLOG2.DATE FROM BLOG2,USER2 WHERE BLOG_AUTHOR_ID=(?) AND BLOG2.BLOG_AUTHOR_ID=USER2.AUTHOR_ID ORDER BY BLOG2.DATE DESC',[current_user.id,])
        # temp=cur.fetchall()
        posts = [
            dict(id=row[0], title=row[1], content=row[2], date=row[3])
            for row in cur.fetchall()
        ]
        return jsonify(posts)
    else:
        return 'Not allowed 2'
    

def send_mail(user,rec):
    token = User.get_reset_token(user)
    sender='flaskblog2003@gmail.com'
    password='invh btjy iynw eedq'
    receiver=rec
    subject='Reset password'
    body=f'''
    <h3>To reset the password, please visit the following link</h3>
     <p>http://127.0.0.1:5000/{url_for('reset_token',token=token,_extrnal=True)}</p>
    <p>If you didn't make this request then ignore this mail and no change will be made.</P>
    <p>Thank you</p>
    '''
    msg = MIMEText(body,'html')
    em=EmailMessage()
    em['From']=sender
    em['To']=receiver
    em['Subject']=subject
    em.set_content(msg)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
        smtp.login(sender,password)
        smtp.sendmail(sender,receiver,em.as_string())

@app.route('/reset_password', methods=['POST'])
def reset_request():
    
    if request.method=='POST':
        request_data = request.get_json()
        if request_data:
            conn = connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM USER2 WHERE EMAIL = (?)', [str(request_data['email']).lower().strip()])
            user = cur.fetchone()
            if user:
                send_mail(user[0],user[2])
                return 'An email has been sent to reset your password'
          
    return 'None'


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    conn = connection()
    cur = conn.cursor()
    if current_user.is_authenticated:
        return 'login successfull 1'
    user = User.verify_reset_token(token)
    if user is None:
        return 'It is an invalid or expired token'
    request_data = request.get_json()
    if request_data:
        new_password = request_data['password']
        cfm_pwd = request_data['cfm_pwd']
        if new_password==cfm_pwd:
            hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')
        # user.password = hashed_pw
            cur.execute('UPDATE USER2 SET PASSWORD = (?) WHERE AUTHOR_ID = (?)', [
                        hashed_pw, user[0]])
            conn.commit()
            return 'Your password has been updated successfully'
            
    return 'None'

@app.errorhandler(404)
def error_handle(e):
    return 'Page not found'

if __name__ == '__main__':
    app.run(port=5000, debug=True)
