from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
#debug mode on
app.config['DEBUG'] = True
#mysql connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blogme@localhost:8889/build-a-blog'
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

    #class constructor -- we use title as a class variable because id will be autoincremented in db?
    def __init__(self, title, body):
        self.title = title
        self.body = body

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
    blog_title = ''
    blog_body = ''
    error_title = ''
    error_body = ''
    if request.method == 'POST':
        blog_title = request.form['blogTitle']
        blog_body = request.form['blogBody']
        if validate_title(blog_title) and validate_body(blog_body):
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            print("--->>> THE NEW BLOG ID IS..." + str(new_blog.id))
            return redirect('/blog?id=' + str(new_blog.id))
        else:
            if not validate_title(blog_title):
                error_title = 'You need a title for your blog entry!'
            
            if not validate_body(blog_body):
                error_body = 'You need content for your blog entry!'

    #tasks = Task.query.all()
    #tasks = Task.query.filter_by(completed = False,owner=owner).all()
    #completed_tasks = Task.query.filter_by(completed = True,owner=owner).all()
 
    return render_template('newpost.html',title='Get It Done!',blog_title=blog_title,blog_body=blog_body,error_title=error_title,error_body=error_body)

if __name__ == '__main__':
    app.run()