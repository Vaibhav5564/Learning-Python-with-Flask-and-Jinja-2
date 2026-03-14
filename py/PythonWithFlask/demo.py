from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea


app = Flask(__name__)

# Secret Key
app.config['SECRET_KEY'] = "722"

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)

# Initialize Migration
migrate = Migrate(app, db)


# Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    content = db.Column(db.Text)
    author = db.Column(db.String(100))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(200))
    
 
# Create a Post Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit", validators=[DataRequired()])

# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    
    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        # Clear The Form
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''
        form.author.data = ''

        # Add Post data to Database
        db.session.add(post)
        db.session.commit()
        
        flash("Blog Post Submitted Successfully")
        
        #Redirect To the WebPage
        
    return render_template("add_post.html", form=form)
        
@app.route('/ShowBlog')
def show():
    posts = Posts.query.order_by(Posts.date_posted).all()
    return render_template("ShowBlog.html", posts=posts)     
        

# Update Blog
@app.route('/update-post/<int:id>', methods=['GET', 'POST'])
def updatepost(id):

    form = PostForm()
    post_to_update = Posts.query.get_or_404(id)

    if form.validate_on_submit():
        post_to_update.title = form.title.data
        post_to_update.author = form.author.data
        post_to_update.slug = form.slug.data
        post_to_update.content = form.content.data

        db.session.commit()
        flash("Post Updated Successfully!")

        return redirect(url_for("updatepost", id=id))

    # Pre-fill form on GET
    if request.method == "GET":
        form.title.data = post_to_update.title
        form.author.data = post_to_update.author
        form.slug.data = post_to_update.slug
        form.content.data = post_to_update.content

    return render_template(
        "UpdateBlog.html",
        form=form,
        post_to_update=post_to_update
    )


# Delete Blog
@app.route('/delete-post/<int:id>', methods=["POST"])
def deletepost(id):

    post_to_delete = Posts.query.get_or_404(id)

    db.session.delete(post_to_delete)
    db.session.commit()

    flash("Post Deleted Successfully")

    return redirect(url_for("show"))


# Json Thing
@app.route('/date')
def get_curr_date():
    fav = {
        "Indoor Game": "Free Fire",
        "Outdoor Game": "Cricket",
        "Hobby": "Spending Time with Family"
    }

    return {
        "Date": date.today(),
        "Favorites": fav
    }


# ----------------------
# Database Model
# ----------------------
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    color = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

   # Password field in database
    password_hash = db.Column(db.String(200))

# Prevent reading the password directly
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # Automatically hash password when setting it
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # Verify password during login
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Representation of object
    def __repr__(self):
        return f"<Name {self.name}>"

with app.app_context():
    db.create_all()


# ----------------------
# Delete Data From Database
# ----------------------

@app.route('/delete/<int:id>', methods=["POST"])
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully")
        
        our_users = Users.query.order_by(Users.date_added).all()

        return redirect(url_for("add_user"))
    
        
    except:
        flash("Ooops! Error Occured")
        return redirect(url_for("add_user"))
    
# ----------------------
# Flask-WTF Form
# ----------------------
class UserForm(FlaskForm):
    name = StringField("Enter Your Name", validators=[DataRequired()])
    email = StringField("Enter Your Email", validators=[DataRequired()])
    color = StringField("Enter Your Favourite Color", validators=[DataRequired()])
    password_hash = PasswordField('Enter Your Password', validators=[DataRequired(), EqualTo('password_hash2', message = 'Password must Match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired ()])
    submit = SubmitField("Submit")


# ----------------------
# Home Page
# ----------------------
@app.route('/')
def index():
    flash("Welcome To Our First Website")
    return render_template("index.html")

# ----------------------
# Add User
# ----------------------
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():

    name = None
    form = UserForm()

    if form.validate_on_submit():

        user = Users.query.filter_by(email=form.email.data).first()

        if user is None:
            hashed_PW = generate_password_hash(form.password_hash.data)
            user = Users(
                name=form.name.data,
                email=form.email.data,
                color=form.color.data,
            )
            
            user.password = form.password_hash.data

            db.session.add(user)
            db.session.commit()

        name = form.name.data

        form.name.data = ""
        form.email.data = ""
        form.color.data = ""
        form.password_hash.data = ""

        flash("User Added Successfully!")

    our_users = Users.query.order_by(Users.date_added).all()

    return render_template(
        "add_user.html",
        form=form,
        name=name,
        our_users=our_users
    )


# ----------------------
# Update User
# ----------------------
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    form = UserForm()
    user_to_update = Users.query.get_or_404(id)

    if form.validate_on_submit():

        user_to_update.name = form.name.data
        user_to_update.email = form.email.data
        user_to_update.color = form.color.data

        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return redirect(url_for("update", id=id))

        except:
            flash("Error! User Not Updated.")

    # Show existing values in form fields
    if request.method == "GET":
        form.name.data = user_to_update.name
        form.email.data = user_to_update.email
        form.color.data = user_to_update.color

    return render_template(
        "update.html",
        form=form,
        user_to_update=user_to_update,
        id=id
    )


# ----------------------
# Members Page
# ----------------------
@app.route('/members')
def members():

    members = Users.query.order_by(Users.date_added).all()

    return render_template(
        "members.html",
        members=members
    )


# ----------------------
# Dynamic User Page
# ----------------------
@app.route('/user')
def user():

    favourite = [
        "Virat Kohli",
        "Rohit Sharma",
        "Cristiano Ronaldo",
        "Roman Reigns"
    ]

    return render_template(
        "user.html",
        f=favourite
    )


# ----------------------
# Contact Page
# ----------------------
@app.route('/contact')
def contact():
    return render_template("contact.html")


# ----------------------
# Error Pages
# ----------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html"), 500


# ----------------------
# Name Page
# ----------------------

class NameForm(FlaskForm):
    name = StringField("Enter Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route('/name', methods=['GET','POST'])
def name_page():

    form = NameForm()
    name = None

    if form.validate_on_submit():
        name = form.name.data
        flash("Form Submitted Successfully")

    return render_template(
        "name.html",
        name=name,
        form=form
    )

# ----------------------
# Create Password Test Page
# ----------------------

class PasswordForm(FlaskForm):
    email = StringField("Enter Your Email", validators=[DataRequired()])
    password_hash = PasswordField("Enter Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route('/test', methods=['GET','POST'])
def test():

    email = None
    password = None
    pw_to_check = None
    passed = None
    
    form = PasswordForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # Clear The Form
        form.email.data = ''
        form.password_hash.data = ''
        
        # Lookup User by Email Adress
        pw_to_check = Users.query.filter_by(email=email).first()
        if pw_to_check == None:
            return render_template("error.html")
        
        passed = check_password_hash(pw_to_check.password_hash, password)
        
    return render_template(
        "test.html",
        email=email,
        pw_to_check=pw_to_check,
        password=password,
        passed=passed,
        form=form
    )



# ----------------------
# Run App
# ----------------------
if __name__ == "__main__":
    app.run(debug=True)
    
    