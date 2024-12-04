
# from alchemy_db import db.Model
from sqlalchemy import  MetaData, ForeignKey
from flask_login import login_user, UserMixin
from sqlalchemy.orm import backref, relationship
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
# from app import app

db = SQLAlchemy()

#from app import login_manager

metadata = MetaData()

#Users class, The class table name 'h1t_users_cvs'
class User(db.Model,UserMixin):


    # __table_args__ = {'extend_existing': True}

    #Create db.Columns
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))
    image = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120),unique=True)
    password = db.Column(db.String(120), unique=True)
    confirm_password = db.Column(db.String(120), unique=True)
    verified = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(120))
    apps = relationship("App_Info",backref="User",lazy=True)
    # project_briefs = relationship("Project_Brief", backref="Project_Brief", lazy=True)

    __mapper_args__={
        "polymorphic_identity":'user',
        'polymorphic_on':role
    }


class company_user(User):

    id = db.Column(db.Integer, ForeignKey('user.id'), primary_key=True)
    contacts = db.Column(db.String(20))
    address = db.Column(db.String(120))
    other = db.Column(db.String(120)) #Resume
    # jobs_applied_for = relationship("Applications", backref='Applications.job_title', lazy=True)
    # hired_user = relationship("hired", backref='Hired Applicant', lazy=True)

    __mapper_args__={
            "polymorphic_identity":'company_user'
        }


class App_Info(db.Model):

    __tablename__ = "app_info"
    #Note: Add new lines from the end and update search results route

    id = db.Column(db.Integer,primary_key=True)
    cid = db.Column(db.Integer,ForeignKey("user.id"))
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    app_category = db.Column(db.String(255))
    platform = db.Column(db.String(20), nullable=False,default="Android")
    version_number = db.Column(db.String(20))
    playstore_link = db.Column(db.String(100),nullable=False)
    ios_link = db.Column(db.String(100))
    uptodown_link = db.Column(db.String(100))
    huawei_link = db.Column(db.String(100))#
    apkpure_link = db.Column(db.String(100))
    galaxy_link = db.Column(db.String(100))
    microsoft_link = db.Column(db.String(100))
    amazon_link = db.Column(db.String(100))
    facebook_link = db.Column(db.String(100))
    whatsapp_link = db.Column(db.String(100))
    x_link = db.Column(db.String(100))
    linkedin_link = db.Column(db.String(100))
    youtube_link = db.Column(db.String(100))
    web_link=db.Column(db.String(100))
    github_link = db.Column(db.String(100))
    app_icon = db.Column(db.String(100))
    app_code = db.Column(db.Integer)
    publish=db.Column(db.Boolean,default=True)
    approved=db.Column(db.Boolean)
    timestamp=db.Column(db.DateTime)
    company_name=db.Column(db.String(100))
    company_contact=db.Column(db.String(100))
    company_email=db.Column(db.String(100))
    edited=db.Column(db.DateTime)
    edited_by=db.Column(db.String(100))
    access=relationship("App_Access_Credits",backref="App_Info",lazy=True)


class App_Access_Credits(db.Model):

    __tablename__ = "app_access_credits"

    id = db.Column(db.Integer,primary_key=True)
    app_id = db.Column(db.Integer,ForeignKey("app_info.id"),unique=True)
    token = db.Column(db.String(255))


class stats_visitors(db.Model):

    __tablename__ = "stats_visitors"

    id = db.Column(db.Integer,primary_key=True)
    user_addr=db.Column(db.String(255))
    device=db.Column(db.String(255))
    browser=db.Column(db.String(255))
    timestamp=db.Column(db.DateTime)

class stats_app_dlink(db.Model):

    __tablename__ = "stats_app_dlink"
    id = db.Column(db.Integer,primary_key=True)
    app_name=db.Column(db.String(255))
    download_link=db.Column(db.String(255))
    # visitor_act=db.Column(db.Integer,ForeignKey("stats_visitors.id"),unique=True)
    user_addr=db.Column(db.String(255))
    device=db.Column(db.String(255))
    browser=db.Column(db.String(255))
    timestamp=db.Column(db.DateTime)


