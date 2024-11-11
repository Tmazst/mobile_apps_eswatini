
from flask import Flask,render_template,url_for,redirect,request,flash,jsonify
from flask_login import login_user, LoginManager,current_user,logout_user, login_required
from sqlalchemy.exc import IntegrityError
from Forms import *
from models import *
from flask_bcrypt import Bcrypt
import secrets
# import MySQLdb
import os
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
# from bs4 import BeautifulSoup as bs
from flask_colorpicker import colorpicker
from image_processor import ImageProcessor
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import itsdangerous
import random
import json
# import sqlite3
# import pymysql
# import pyodbc

import mysql.connector



#Change App
app = Flask(__name__)
app.config['SECRET_KEY'] = "sdsdjfe832j2rj_32j"
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///eswatiniapps_db.db"
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:tmazst41@localhost/eswatini_apps_db" #?driver=MySQL+ODBC+8.0+Driver"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://techtlnf_tmaz:!Tmazst41#@localhost/techtlnf_apps_eswatini"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle':280}
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOADED"] = 'static/uploads'

# Initialise App with DB 
db.init_app(app)

application = app

#Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

if os.path.exists('client.json'):
    # Load secrets from JSON file
    with open('client.json') as f:
        creds = json.load(f)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



def process_file(file):
        global img_checker
        # img_checker = Dont_Update
        # Avoid duplication of same image in a session 
        # if img_checker.img  == file.filename:
        #     print("File updated")
        #     return img_checker.cur_file
        # else:
        
        filename = secure_filename(file.filename)

        # img_checker.img = file.filename

        _img_name, _ext = os.path.splitext(file.filename)
        gen_random = secrets.token_hex(8)
        new_file_name = gen_random + _ext

        print("DEBIG IMAGE: ",new_file_name)

        if file.filename == '':
            return 'No selected file'

        if file.filename:
            file_saved = file.save(os.path.join("static/images",new_file_name))
            flash(f"File Upload Successful!!", "success")
            return new_file_name

        # else:
        #     return f"Allowed are [ .png, .jpg, .jpeg, .gif] only"

ser = Serializer(app.config['SECRET_KEY']) 

#Database Tables Updates
def createall(db):
    db.create_all()

#Password Encryption
encrypt_password = Bcrypt()

#Populating variables across all routes
@app.context_processor
def inject_ser():
   
     # Define or retrieve the value for 'ser'

    return dict(ser=ser)


@app.route("/", methods=['POST','GET'])
def home():
    layout = None
    db.create_all()
    apps = App_Info.query.all()

    for app in apps:
        print("APP CODES 7 NM: ",app.app_code,"NM",app.name)

    categories= {app.app_category for app in apps}

    if request.args.get('icon'):
        layout = request.args.get('icon')


    return render_template("index.html", apps=apps, layout=layout, categories=categories)


@app.route("/about", methods=['POST','GET'])
def about():

    return render_template("about.html")

def send_email(app_info):
    
    def send_veri_mail():

        app.config["MAIL_SERVER"] = "smtp.googlemail.com"
        app.config["MAIL_PORT"] = 587
        app.config["MAIL_USE_TLS"] = True
        # Creditentials saved in environmental variables
        em = app.config["MAIL_USERNAME"] ='pro.dignitron@gmail.com' # os.getenv("MAIL")  creds.get('email')
        pwd = app.config["MAIL_PASSWORD"] = creds.get('gpass')  # os.getenv("PWD")
        app.config["MAIL_DEFAULT_SENDER"] = "noreply@gmail.com"

        mail = Mail(app)
        ser = Serializer(app.config['SECRET_KEY']) 
        token = ser.dumps({"data":app_info.id})

        try:
            app_access=App_Access_Credits.query.filter_by(app_id=app_info.id).first()
            if app_access:
                app_access.token=token
                db.session.commit()
            else:
                db.session.add(App_Access_Credits(app_id=app_info.id,token=token))
                db.session.commit()

        except IntegrityError:
            db.session.rollback()
        
        msg = Message(subject="Testing", sender="no-reply@gmail.com", recipients=[em])

        msg.html = f"""<html> 
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <style>
           
           body{{background-color: #e0e0e0;font-family: "Roboto" ,"Times New Roman";}}
           .mail-container{{width:60%;background-color: #ffffff;border-radius: 20px;margin:20px auto;  padding: 25px;}}
           .header{{height:100px;display: flex;justify-content: space-around;padding:15px;margin-bottom:80px ;}}
           .sub-titles{{background-color: #c4c4c4;color:white;padding:5px 10px;border-radius: 15px;font-weight: 600;font-size: 16px;}}
           p,label,small{{color:rgb(53, 53, 53)}}
           .content{{color:rgb(53, 53, 53)}}
           .scroll-container{{display: flex;justify-content: flex-start;gap:10px;align-items:center;width:max-content;}}
           .app-container{{display: flex;justify-content: center;align-items: center;flex-direction: column;width:200px;min-height: 200px;
                            gap:5px;padding:25px;border:1px solid grey;border-radius: 25px;}}
            .icon-cont img{{width:100%;border: 1px solid rgb(235, 235, 235);}}
            .app-name{{font-weight:500;font-size:23px;text-align: center;}}
            .owner-name{{font-weight:500;font-size:16px;color:#134f72;display: flex;align-items: center;}}
            .icon-imgs{{transition: all 0.3s ease;height: 30px;}}
            .icon-imgs:hover{{transform:scale(1.5)}}
            .description{{font-size:12px;color:#606060;text-align: center;}}
            .btns{{padding:10px;color:coral;border-radius:20px;border:1px solid coral;font-size: 16px;background: none;min-width:70px;  
                text-align: center;}}
            .btns:hover{{border:1px solid rgb(117, 117, 117) !important;color:rgb(117, 117, 117) !important;cursor: pointer;}}
            a{{text-decoration: none;}}
            .bolden{{font-weight:600}}
            img{{border-radius: 15px;}}
            .general-flex{{display:flex;justify-content:flex-start;align-items:center;gap:10px;flex-wrap:wrap;}}
            .mail-links{{display: flex;align-items: center;}}
            .mail-links span{{font-weight:600;font-size: 13px;color:#134f72}}
            .sign-column{{}}
            .email-sign-cont{{background-color: #f7f6f6;border-radius: 20px;padding:15px}}
            .div-line{{background-color: white;border-radius: 10px;width:7px;height:150px}}
            .services{{font-weight: 600;color:#134f72;font-size: 20px;}}
            .service{{font-weight: 500;color:#49565e}}
            .app-container {{width: 200px;min-height: 200px;border: 1px solid grey;border-radius: 25px;padding: 25px;background-color: #fff;
                overflow: hidden; /* Clear floats within the container */
            }}
            .app-cell {{
            text-align: center; /* Center the text */
        }}
        </style>
    </head>
    <body>
        <div style="width:60%;background-color: #ffffff;border-radius: 20px;margin:20px auto;  padding: 25px;"  class="mail-container">
            <!-- Header Title  -->
            <div class="header">
                <img style="height: inherit;" src="https://techxolutions.com/images/logo.png" alt="Image"" /> <img style="height: inherit;" src="https://techxolutions.com/images/eswatini_flag.png" /> 
            </div>
            <!-- Subject  -->
            <div class="subject">
               <span class="sub-titles" style="background-color: #c4c4c4;color:white;padding:5px 10px;border-radius: 15px;font-weight: 600;font-size: 16px;">Subject</span> <span style="font-size: large;">Showcase Your App on Our New Platform!</span>
            </div><br><br>
            <!-- Body Message  -->
            <section style="flex-wrap: nowrap;padding:10px" class="">
                <!-- Greeting Message  -->
                <h3 style="color:#00a550;">Good day,</h3>
                <div style="color:rgb(53, 53, 53)" class="content">My name is Thabo Maziya, and I am reaching 
                    out on behalf of Tech Xolutions(TechX). We are launching a new initiative "TechConnectPlus" aimed at enhancing
                    the visibility and accessibility of mobile applications developed in Eswatini, with a focus on better service delivery for EmaSwati.
                </div><br>
                <div style="color:rgb(53, 53, 53)" class="content"> We believe that your app {app_info.name} significantly contributes to the needs of Eswatini
                    community and would like to feature it prominently on our centralized platform. 
                    This platform serve as a repository where users can easily discover and explore mobile applications 
                    that cater to their service requirements. 
                </div>
                
                
        


                <!-- Link  -->
                <div style="margin:20px auto;width:max-content"><span>Please Visit TechConnect Plus here:</span><a href="https://eswatiniapps.techxolutions.com"><span style="background-color: #00a550;color:white;padding:5px 10px;border-radius: 15px;font-weight: 600;font-size: 16px;" class="sub-titles">website</span></div></a>
                <br><br>
                <div style="width:60%;margin:10px auto" class="content objectives">
                    <!-- Sub Topic  -->
                    <h2 style="color:coral">Key Objects of the Project</h2>
                    <p style="vertical-align: top;"><span><img style="height:20px" src="https://techxolutions.com/images/tick-icon.png" /></span>
                        <span style="" class="bolden">Increased Awareness:</span><span >Our goal is to promote awareness among EmaSwati about diverse mobile applications, encouraging user engagement with these essential digital solutions.
                        </span></p>
                    <p><span><img style="height:20px" src="https://techxolutions.com/images/tick-icon.png" /></span>
                        <span class="bolden">Centralized Hub:</span> <span>Users will have streamlined access to a variety of apps, making it easy for them to locate the resources they need.
                    </span></p><br><br>
                <!-- Sub Topic  -->
                <h2 style="color:coral">App Verification Details</h2>
                <p  class="bolden">We invite you to verify and enhance the details of your app as it will be listed on our site. Should you wish to modify any information or links associated with your app and should you opt to<span style="color:blue"><a href="{url_for('app_form_edit', token=token, _external=True)}"> unpublish</a></span> it from this site, we have provided
                  a link below necessary to do so.
                </p>
                <!-- List  -->
                <div>
                <p style="vertical-align: top;"><span><img style="height:20px" src="https://techxolutions.com/images/tick-icon.png" /></span>
                <span style="" class="bolden">App Name:</span><span >{app_info.name}</span></p>
                </div>
                <div>
                <p style="vertical-align: top;"><span><img style="height:20px" src="https://techxolutions.com/images/tick-icon.png" /></span>
                    <span style="" class="bolden">Category:</span><span >{app_info.app_category}</span></p>
                </div>
                <div>
                <p style="vertical-align: top;"><span><img style="height:20px" src="https://techxolutions.com/images/tick-icon.png" /></span>
                    <span style="" class="bolden">Description:</span><span >{app_info.description}</span></p>
                </div>
                <div>
                <p style="vertical-align: top;"><span><img style="height:20px" src="https://techxolutions.com/images/tick-icon.png" /></span>
                    <span style="" class="bolden">Google PlayStore Link:</span><span >{app_info.playstore_link}</span></p>
                    </div><br>
                <!-- Link  -->
                <div style="margin:20px auto;width:"><span>Edit App Details Here:</span><a style="text-decoration:none" href="{url_for('app_form_edit', token=token, _external=True)}">
                <span style="background-color: #00a550;color:white;padding:5px 10px;border-radius: 15px;font-weight: 600;font-size: 16px;" class="sub-titles">App Info</span></a></div>
                <!-- Footer / Email Signature -->
                <p style="font-weight:600;font-size:13px">Note:<span style="font-weight:400">App Name, Description, Icon, and Links are sourced from Google Play Store.</span></p>
                </div><br><br>


                <p  class="">Kind Regards,</p> 
                <table style="font-size: medium;background-color: #f1f1f1;width:100% !important;background-color: #f7f6f6;border-radius: 20px;padding:15px" class="email-sign-cont ">
                    <tr style="font-size: medium;width:100% !important" >
                        <td style="vertical-align: top;" class="sign-column">
                            <span style="font-size: large;font-weight: 600;color:#606060">Thabo Maziya</span>
                            <span style="font-size: large;font-weight: 600;color:#606060">Developer</span>
                            <div class="mail-links"><img style="height:25px" src="http://techxolutions.com/images/email_icon.png"/><span>thabo@techxolutions.com</span></div>
                            <div class="mail-links"><img style="height:25px" src="http://techxolutions.com/images/telephone_icon.png"/><span>(+687) 7641 2255</span></div>
                        </td>
                        <td style="vertical-align: top;" class="sign-column">
                            <div style="font-weight: 600;color:#134f72;font-size: 20px;" class="services">Tech Xolutions(TechX)</div>
                            <div class="services">Our Services</div>
                            <div class="service">Web Design & Development</div>
                            <div class="service">Graphic Design</div>
                            <div class="service">Engraving</div>
                        </td>
                        <td style="vertical-align: top;" class="sign-column">
                            <img style="height:150px;width:180px" src="http://techxolutions.com/images/Techx_logo.png" />
                        </td>
                    </tr>
                </table><br><br>
                
            </section>
            <div style="" class="email-signature">

            </div>
        </div>

        <script>
        
        </script>
    </body>
"""

        try:
            mail.send(msg)
            flash(f'Email Sent Successfully!', 'success')
            return "Email Sent"
        except Exception as e:
            flash(f'Email not sent here', 'error')
            return "The mail was not sent"

    # try:
    send_veri_mail() 


@app.route("/send_email", methods=['POST','GET'])
def email():
    app_name_rq = None
    email_form = SendEmailForm()

    if request.method == "POST":
        app_name = email_form.app_name.data

        if app_name:
            app_name_rq = App_Info.query.filter_by(name=app_name).first()

        if app_name_rq:
            send_email(app_name_rq)
        else:
            return jsonify({"Error":f"App Name {app_name_rq} Does Not Exists in the System"})

    return render_template("send_email.html",email_form=email_form)


@app.route("/app_form", methods=['POST','GET'])
def app_form():

    app_form = App_Info_Form()

    if request.method == "POST" :#and app_form.validate_on_submit()
        appinfo = App_Info(
            name = app_form.name.data,description = app_form.description.data,
            version_number = app_form.version_number.data,playstore_link = app_form.playstore_link.data,
            facebook_link = app_form.facebook_link.data,whatsapp_link = app_form.whatsapp_link.data,
            x_link = app_form.x_link.data,linkedin_link = app_form.linkedin_link.data,
            youtube_link = app_form.youtube_link.data, web_link=app_form.web_link.data,
            github_link = app_form.github_link.data,company_name = app_form.company_name.data,company_contact = app_form.company_contact.data
            ,company_email = app_form.company_email.data,ios_link = app_form.ios_link.data,uptodown_link = app_form.uptodown_link.data,
            app_category = app_form.app_category.data,timestamp=datetime.now(),app_code=datetime.now().microsecond,huawei_link = app_form.huawei_link.data,apkpure_link=app_form.apkpure_link.data
        )

        # img = process_file(app_form.app_icon.data)
        if app_form.app_icon.data:
            appinfo.app_icon = process_file(app_form.app_icon.data)

        # Check Code does not exists 
        validate_apc = App_Info.query.filter_by(app_code= appinfo.app_code).first()

        if validate_apc:
            appinfo.app_code = datetime.now().microsecond
            db.session.add(appinfo)
            db.session.commit()
        else:
            db.session.add(appinfo)
            db.session.commit()

        flash("Successful","success")

    return render_template("app_form.html",app_form=app_form)


@app.route("/edit_app", methods=['POST','GET'])
def edit_app():

    edit_app = EditAppInfoForm()

        # if request.args.get('id'): se
    if request.method == 'POST':

        print("Debeug Get Req. from form: ",edit_app.app_code.data ," ",edit_app.app_name.data)

        code_ = ser.dumps({"data":edit_app.app_code.data})

        # print("Debeug Get Req. from form: ",code_)

        return redirect(url_for("app_form_editor",app_name=edit_app.app_name.data,code=code_))

    return render_template("edit_app.html",edit_app=edit_app)

class Save_Values:
    app_obj=None


@app.route("/app_form_editor", methods=['POST','GET'])
def app_form_editor(app_name=None,code=None):
    # app_info=None
    app_form_update = App_Info_Form()

    if request.method == "GET" and request.args.get("code"):
        app_info=App_Info.query.filter_by(app_code=ser.loads(request.args.get("code")).get('data'),name=request.args.get("app_name")).first()
        # Save_Values.app_obj=app_info

    # if not Save_Values.app_obj:
    #     return jsonify({"Error":"Looks like something went wrong with the URL request, Please request a new link"})

    if request.method == "POST":
        app_info = App_Info.query.filter_by(app_code=ser.loads(request.args.get("code")).get('data'),name=request.args.get("app_name")).first()
        if app_form_update.name.data:
            app_info.name = app_form_update.name.data
        if request.form.get("description"):
            app_info.description = request.form.get("description").strip()
        if app_form_update.version_number.data:
            app_info.version_number = app_form_update.version_number.data
        if app_form_update.app_category_ed.data:
            app_info.app_category = app_form_update.app_category_ed.data
        if app_form_update.playstore_link.data:
            app_info.playstore_link = app_form_update.playstore_link.data
        if app_form_update.facebook_link.data:
            app_info.facebook_link = app_form_update.facebook_link.data
        if app_form_update.whatsapp_link.data:
            app_info.whatsapp_link = app_form_update.whatsapp_link.data
        app_info.x_link = app_form_update.x_link.data
        if app_form_update.linkedin_link.data:
            app_info.linkedin_link = app_form_update.linkedin_link.data
        if app_form_update.youtube_link.data:
            app_info.youtube_link = app_form_update.youtube_link.data
        if app_form_update.web_link.data:
            app_info.web_link=app_form_update.web_link.data
        if app_form_update.github_link.data:
            app_info.github_link = app_form_update.github_link.data
        if app_form_update.huawei_link.data:
            app_info.huawei_link = app_form_update.huawei_link.data
        if app_form_update.apkpure_link.data:
            app_info.apkpure = app_form_update.apkpure_link.data
        if app_form_update.company_name.data:
            app_info.company_name = app_form_update.company_name.data
        if app_form_update.company_contact.data:
            app_info.company_contact = app_form_update.company_contact.data
        if app_form_update.company_email.data:
            app_info.company_email = app_form_update.company_email.data

        app_info.publish = app_form_update.publish.data

        if app_form_update.app_icon.data:
            print("Check if there is data:",app_form_update.app_icon.data )
            img_update = app_form_update.app_icon.data
            app_info.app_icon = process_file(img_update)

        db.session.commit()
        flash("Update Successful","success")
        return redirect(url_for("home"))
        

    return render_template("app_form_edit.html",app_form_update=app_form_update,app_info=app_info)


@app.route("/app_form_edit/<token>", methods=['POST','GET'])
def app_form_edit(token):
    id_=None
    app_form_update = App_Info_Form()
    print("DEBUG EMAIL TOKEN LINK: ",token)
    if token:
        id_obj = App_Access_Credits.query.filter_by(token=token).first()
        id_ = id_obj.app_id

    app_info =App_Info.query.get(id_)

    if not app_info:
        return jsonify({"Error":"Looks like something went wrong with the URL Request, Please request a new link"})

    if request.method == "POST" and app_info:
        if app_form_update.name.data:
            app_info.name = app_form_update.name.data
        if request.form.get("description"):
            app_info.description = request.form.get("description").strip()
        if app_form_update.version_number.data:
            app_info.version_number = app_form_update.version_number.data
        if app_form_update.app_category_ed.data:
            app_info.app_category = app_form_update.app_category_ed.data
        if app_form_update.playstore_link.data:
            app_info.playstore_link = app_form_update.playstore_link.data
        if app_form_update.facebook_link.data:
            app_info.facebook_link = app_form_update.facebook_link.data
        if app_form_update.whatsapp_link.data:
            app_info.whatsapp_link = app_form_update.whatsapp_link.data
        app_info.x_link = app_form_update.x_link.data
        if app_form_update.linkedin_link.data:
            app_info.linkedin_link = app_form_update.linkedin_link.data
        if app_form_update.youtube_link.data:
            app_info.youtube_link = app_form_update.youtube_link.data
        if app_form_update.web_link.data:
            app_info.web_link=app_form_update.web_link.data
        if app_form_update.github_link.data:
            app_info.github_link = app_form_update.github_link.data
        if app_form_update.huawei_link.data:
            app_info.huawei_link = app_form_update.huawei_link.data
        if app_form_update.apkpure_link.data:
            app_info.apkpure = app_form_update.apkpure_link.data
        if app_form_update.company_name.data:
            app_info.company_name = app_form_update.company_name.data
        if app_form_update.company_contact.data:
            app_info.company_contact = app_form_update.company_contact.data
        if app_form_update.company_email.data:
            app_info.company_email = app_form_update.company_email.data

        app_info.publish = app_form_update.publish.data

        if app_form_update.app_icon.data:
            print("Check if there is data:",app_form_update.app_icon.data )
            img_update = app_form_update.app_icon.data
            app_info.app_icon = process_file(img_update)

        db.session.commit()
        flash("Update Successful","success")

    return render_template("app_form_edit.html",app_form_update=app_form_update,app_info=app_info)


@app.route("/vac_signup", methods=["POST","GET"])
def sign_up():

    register = Register()
    user = None

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':

        if register.validate_on_submit():    

            hashd_pwd = encrypt_password.generate_password_hash(register.password.data).decode('utf-8')

            if register.company_signup.data:
                user = company_user(name=register.name.data, email=register.email.data, password=hashd_pwd,
                        confirm_password=hashd_pwd,image="logo_template.png",company_contacts=register.contacts.data,role = 'company_user',
                        timestamp=datetime.now())
            # else:
            #     user = vacationer_user(name=register.name.data, email=register.email.data, password=hashd_pwd,
            #             confirm_password=hashd_pwd,image="default.jpg",contacts=register.contacts.data,
            #             timestamp=datetime.now(timezone.utc),role = 'vacationer_user')
                             
            # print('Role Checked!: ',user.role)

            # try:
            if not Register().validate_email(register.email.data):
                db.session.add(user)
                db.session.commit()
                print('Sign up successful!')
                flash(f"Account Successfully Created for {register.name.data}", "success")
            else:
                flash(f"Something went wrong, check for errors", "error")
                print('Sign up unsuccessful')
            return redirect(url_for('login'))
            # except: # IntegrityError:
            #     pass

        elif register.errors:
            flash(f"Account Creation Unsuccessful ", "error")
            print(register.errors)

    # from myproject.models import user
    return render_template("vac-signup-form.html",register=register)

@app.route('/search', methods=['GET'])
def search_in_table():

    apps_obj = App_Info()

    search_value = request.args.get('search_value')
    table_name = "app_info"  # request.args.get('table_name')

    # Database connection parameters
    db_config = {
        'user': creds['user'],
        'password': creds['db_pass'],
        'host': 'localhost',  # or your MySQL server address
        'database': 'techtlnf_apps_eswatini'
    }

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Use parameters to avoid SQL injection
    query = f"SELECT * FROM `{table_name}` WHERE CONCAT(COALESCE(name, ''), COALESCE(company_name, ''), COALESCE(app_category, ''), COALESCE(platform, ''))  LIKE %s"
    cursor.execute(query, ('%' + search_value + '%',))
    rows = cursor.fetchall()

    # Print results for debugging
    for row in rows:
        print("Car Make: ", row)

    # Convert the results to a list of dictionaries (depending on your needs)
    apps = [{'id': row[0], 'cid': row[1], 'name': row[2], 'description': row[3], 'app_category': row[4], 
             'platform': row[5], 'version_number': row[6], 'playstore_link': row[7], 'ios_link': row[8],'uptodown_link': row[9],
             'huawei_link': row[10], 'apkpure_link': row[11], 'galaxy_link': row[12],'microsoft_link': row[13], 'amazon_link': row[14], 
               'facebook_link': row[15], 'whatsapp_link': row[16], 'x_link': row[17],'linkedin_link': row[18], 'youtube_link': row[19], 'web_link': row[20],
            'github_link': row[21], 'app_icon': row[22], "app_code":row[23],'publish': row[24],'approved': row[25], 'timestamp': row[26], 'company_name': row[27],
            'company_contact': row[28],'company_email': row[29],} for row in rows]

    cursor.close()
    conn.close()

    return render_template('search_results.html', apps_obj=apps_obj, apps=apps,search_value=search_value)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


