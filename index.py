from flask import Flask,render_template,redirect,url_for,request,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import Integer, String,ForeignKey
import string,random

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)

class Urls(db.Model):
    id = mapped_column(Integer,autoincrement=True,primary_key=True)
    long_url = mapped_column(String(100),nullable=False)
    short_url = mapped_column(String(6),unique=True,nullable=False)

with app.app_context():
    db.create_all()

def shorten_url():
    char = string.ascii_letters + string.digits
    short_url = ""
    for i in range(6):
        short_url += "".join(random.choice(char))
    return short_url

@app.route('/', methods = ["GET","POST"])
def index():
    if request.method == "POST":
        long_url = request.form.get("long_url")
        existing_url = Urls.query.filter_by(long_url=long_url).first()
        if existing_url:
            flash(f'your shorted url:{request.host_url}{existing_url.short_url}','info')
            return redirect(url_for("index"))

        short_url = shorten_url()
        while Urls.query.filter_by(short_url=short_url).first() is not None:
            short_url = shorten_url()
        
        new_url = Urls(long_url = long_url,short_url=short_url)
        db.session.add(new_url)
        db.session.commit()
        flash(f'your shorted url:{request.host_url}{short_url}','success')
        return redirect(url_for("index"))
    return render_template("index.html")

@app.route('/<short_url>')
def direction(short_url):
    url = Urls.query.filter_by(short_url=short_url).first_or_404()
    return redirect(url.long_url)