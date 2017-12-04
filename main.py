from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
#debug mode on
app.config['DEBUG'] = True
#mysql connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:NJs5TxIsfyUdUkIP@localhost:8889/get-it-done'
#for mysql troubleshooting
app.config['SQLALCHEMY_ECHO'] = True

#create new object by passing flask app to SQLALCHEMY
db = SQLAlchemy(app)

#create a secret key for session use
app.secret_key = 'y337kGcys&zpb3'

#class that represents persistent application data (class extends db.model)
class Task(db.Model):

    #set up primary key column -- id
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)
    #link user to task
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #class constructor -- we use name as a class variable because id will be autoincremented in db?
    def __init__(self, name, owner):
        self.name = name
        self.completed = False
        self.owner = owner

class User(db.Model):
    #primary key column -- id
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    #tasks list is populated with tasks from Task with owner
    tasks = db.relationship('Task', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

#run this function before any request
@app.before_request
def require_login():
    #allowed_routes = pages that don't require a session to login
    allowed_routes = ['login', 'register']
    '''
    request.endpoint is the page requested. the endpoint is checked against the
    allowed_routes list. If not in allowed_routes, session is checked. If email is
    not in session, login page is invoked
    '''
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        '''
        return user data from database (User table). We expect only one email (since it is unique), so tell it to return the first record
        it finds (this is equivalent to a fetch 1 rows statement in db2). This statement ends the query after the first email is found,
        rather than completing the table scan - so it may save us a few cpu cycles.
        '''
        user = User.query.filter_by(email=email).first()
        #if there is a user, and user.password == the password from the form, let the user login
        if user and user.password == password:
            #TODO - "remember" that the user has logged in
            session['email'] = email
            flash("Logged In")
            return redirect('/')
        else:
            #TODO - msg to explain why login failed
            flash('User password incorrect, or user does not exist', 'error')
            

    return render_template("login.html")

@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verifyPassword']

        #TODO - validate user data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            #TODO - remember the user
            session['email'] = email
            return redirect('/')
        else:
            #TODO - user better response messaging
            flash('This user already exists', error)


    return render_template("register.html")

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route("/", methods=['POST', 'GET'])
def index():

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name, owner)
        db.session.add(new_task)
        db.session.commit()

    #tasks = Task.query.all()
    tasks = Task.query.filter_by(completed = False,owner=owner).all()
    completed_tasks = Task.query.filter_by(completed = True,owner=owner).all()
 
    return render_template('todos.html',tasks=tasks,title='Get It Done!',completed_tasks=completed_tasks)

@app.route("/delete-task", methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    #db.session.delete(task)
    db.session.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run()