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

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    post_id = request.args.get('id')
    if post_id:
        #int_id = int(form_value)
        post = Blog.query.filter_by(id=post_id).first()
        return render_template('blog_entry.html',post=post)
    else:
        posts = Blog.query.all()
        return render_template('blog.html',posts=posts,title='Build a Blog')
        
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
                error_title = 'You need a title for your blog entry!'
            
            if not validate_body(blog_body):
                error_body = 'You need content for your blog entry!'

    #tasks = Task.query.all()
    #tasks = Task.query.filter_by(completed = False,owner=owner).all()
    #completed_tasks = Task.query.filter_by(completed = True,owner=owner).all()
 
    return render_template('newpost.html',title='Blogz',blog_title=blog_title,blog_body=blog_body,error_title=error_title,error_body=error_body)

@app.route("/login", methods=['POST', 'GET'])
def login():

    username_error = ""
    password_error = ""
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
                username_error = "User does not exist, please re-enter or register for new account"
            else:
                password_error = "Password is incorrect, please re-enter"

    return render_template('login.html',username_error=username_error,password_error=password_error)

@app.route("/signup", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verifyPassword']

        #TODO - validate user data

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
            flash('This user already exists', 'error')
    
    return render_template("signup.html")





if __name__ == '__main__':
    app.run()