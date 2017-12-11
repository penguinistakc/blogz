from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
#debug mode on
app.config['DEBUG'] = True
#mysql connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzme@localhost:8889/blogz'
#for mysql troubleshooting
app.config['SQLALCHEMY_ECHO'] = True

#create new object by passing flask app to SQLALCHEMY
db = SQLAlchemy(app)

#create a secret key for session use
app.secret_key = 'mj893sk&56p'

#class that represents persistent application data (class extends db.model)
class Blog(db.Model):

    #set up primary key column -- id
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(240))
    body = db.Column(db.String(480))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #class constructor -- we use title as a class variable because id will be autoincremented in db?
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
        

class User(db.Model):
    #primary key column -- id
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    #blogs list is populated with blogs from Blog with owner
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    #allowed routes
    allowed_routes = ['login','list_blogs','signup','index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():

    post_id = request.args.get('id')
    user = request.args.get('user')
    if post_id:
        post = Blog.query.filter_by(id=post_id).first()
        return render_template('blog_entry.html',post=post)
    elif user:
        user_id = User.query.filter_by(username=user).first()
        posts = Blog.query.filter_by(owner_id=user_id.id).all()
        return render_template('blog.html',posts=posts,title='Blogz')
    else:
        posts = Blog.query.all()
        return render_template('blog.html',posts=posts,title='Blogz')
        
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()
    blog_title = ''
    blog_body = ''
    error_title = ''
    error_body = ''
    if request.method == 'POST':
        blog_title = request.form['blogTitle']
        blog_body = request.form['blogBody']
        if validate_title(blog_title) and validate_body(blog_body):
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            #print("--->>> THE NEW BLOG ID IS..." + str(new_blog.id))
            return redirect('/blog?id=' + str(new_blog.id))
        else:
            if not validate_title(blog_title):
                flash('You need a title for your blog entry!','error')
            
            if not validate_body(blog_body):
                flash('You need content for your blog entry!','error')

    #tasks = Task.query.all()
    #tasks = Task.query.filter_by(completed = False,owner=owner).all()
    #completed_tasks = Task.query.filter_by(completed = True,owner=owner).all()
 
    return render_template('newpost.html',title='Blogz',blog_title=blog_title,blog_body=blog_body,error_title=error_title,error_body=error_body)

@app.route("/login", methods=['POST', 'GET'])
def login():

    username = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        '''
        return user data from database (User table). We expect only one email (since it is unique), so tell it to return the first record
        it finds (this is equivalent to a fetch 1 rows statement in db2). This statement ends the query after the first email is found,
        rather than completing the table scan - so it may save us a few cpu cycles.
        '''
        user = User.query.filter_by(username=username).first()
        #if there is a user, and user.password == the password from the form, let the user login

        if user and user.password == password:
            #TODO - "remember" that the user has logged in
            session['username'] = username
            flash("Logged In")
            return redirect('/newpost')
        else:
            if not user:
                user_error = 'User {} does not exist, please re-enter or register for new account'.format(username)
                flash(user_error, 'error')
                username = ''
            else:
                flash('Password is incorrect, please re-enter', 'error')
                

    return render_template('login.html',username=username)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route("/signup", methods=['POST', 'GET'])
def register():
    username = ''
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verifyPassword']

        #TODO - validate user data
        if validate_signup(username, password, verify):
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                #TODO - remember the user
                session['username'] = username
                return redirect('/newpost')
            else:
                #TODO - user better response messaging
                user_error = 'User {} already exists'.format(username)
                flash(user_error, 'error')
                username = ''
    
    return render_template('signup.html',username=username)

@app.route("/")
def index():
    users = User.query.all()
    return render_template('index.html',users=users)

def validate_signup(username, password, verification):
    validated = True
    if field_not_empty(username) and field_not_empty(password) and field_not_empty(verification):
        if not validate_username(username):
            validated = False
        if not validate_password(password, verification):
            validated = False
    else:
        flash('One or more fields are invalid - all three fields must be populated', 'error')
        validated = False

    return validated

def validate_username(username):
    if field_has_min_chars(username):
        return True
    else:
        flash('Username must have at least 3 characters. Please re-enter.','error')
    return False

def validate_password(password, verify):
    if field_has_min_chars(password):
        if verify == password:
            return True
        else:
            flash('Passwords do not match','error')
            
    else:
        flash('Password must have at least 3 characters','error')


    return False

def field_not_empty(data):
    has_data = data.strip()
    if has_data:
        return True

    return False

def field_has_min_chars(data):
    has_data = data.strip()
    if len(has_data) < 3:
        return False

    return True

def validate_title(title):
    has_data = title.strip()
    if not has_data:
        #flash('Your blog entry requires a title!', 'error')
        return False
            
    return True

def validate_body(body):
    has_data = body.strip()
    if not has_data:
        #flash('You forgot the blog entry!', 'error')
        return False
        

    return True




if __name__ == '__main__':
    app.run()