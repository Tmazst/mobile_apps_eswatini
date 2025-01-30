
from flask import Flask,render_template,url_for,redirect,request,flash,jsonify,make_response,session
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
from authlib.integrations.flask_client import OAuth
# from bs4 import BeautifulSoup as bs
from flask_colorpicker import colorpicker
from image_processor import ImageProcessor
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import itsdangerous
import random
import json
from PIL import Image
import re
# import sqlite3
# import pymysql
# import pyodbc

import mysql.connector
import user_agents


#Change App
app = Flask(__name__)
app.config['SECRET_KEY'] = "sdsdjfe832j2rj_32j"
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///eswatiniapps_db.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:tmazst41@localhost/images_hub_db" #?driver=MySQL+ODBC+8.0+Driver"
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://techtlnf_tmaz:!Tmazst41#@localhost/techtlnf_apps_eswatini"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle':280}
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOADED"] = 'static/uploads/usr_images'
app.config["THUMBS"] = 'static/uploads/usr_images/thumbnails'


oauth = OAuth(app)
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

def compress_image(image_path, target_size_kb):
    #e.g. static/images/usr_images/sipho_2/thumbs
    thumbnail_dir = app.config["THUMBS"]

    if not os.path.exists(thumbnail_dir):
        os.makedirs(thumbnail_dir)

    # Open an image file
    with Image.open(image_path) as img:

        # try:
        img = img.convert('RGB')  # Convert to RGB for compatibility with JPEG
        # if img.mode in ('RGBA', 'LA'):
        #     img = img.convert('RGB')  # Convert to RGB
        # elif img.mode == 'L':
        #     img = img.convert('L')  # Convert to L if you want to keep it grayscale without alpha

        # Calculate quality based on the target size
        quality = 85  # Starting quality

        while True:
            print("Debug Co,pression: ",image_path,thumbnail_dir)
            file = os.path.basename(image_path)
            # Save to a temporary file to check the size
            # temp_file = image_path.replace(os.path.splitext(image_path)[1], "_temp.jpg")
            img.save(os.path.join(thumbnail_dir,file), format='JPEG', quality=quality)

            # Check size
            if os.path.getsize(thumbnail_dir) <= target_size_kb * 1024:  # Convert KB to bytes
                break
            quality -= 5  # Decrease quality to reduce file size

            if quality < 10:  # Minimum quality threshold
                break

            # Move the temp file to the original file name or save as a new file
            # os.replace(temp_file, image_path)
            
        # except Exception as e:
        #     print(f"Error standardizing image input: {e}")
        #     return None 

def process_file(file,usr):
        global img_checker
        target_size = 90
        
        filename = secure_filename(file.filename)

        file_path = os.path.join(app.config["UPLOADED"])

        #static/images/usr_images
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        _img_name, _ext = os.path.splitext(file.filename)
        gen_random = secrets.token_hex(8) + "_" + str(usr.id)
        new_file_name = gen_random + _ext

        print("DEBIG IMAGE: ",new_file_name)

        if file.filename == '':
            return 'No selected file'

        if file.filename:
            new_path =os.path.join(file_path,new_file_name)
            file_saved = file.save(new_path)
            compress_image(new_path,target_size_kb=90)
            flash(f"File Upload Successful!!", "success")

            return new_file_name

        # else:
        #     return f"Allowed are [ .png, .jpg, .jpeg, .gif] only"

if os.path.exists('client.json'):
    appConfig = {
        "OAUTH2_CLIENT_ID" : creds['clientid'],
        "OAUTH2_CLIENT_SECRET":creds['clientps'],
        "OAUTH2_META_URL":"",
        "FLASK_SECRET":"sdsdjsdsdjfe832j2rj_32jfesdsdjfe832j2rj32j832",
        "FLASK_PORT": 5000  
    }


    oauth.register("appenda_oauth",
                client_id = appConfig.get("OAUTH2_CLIENT_ID"),
                client_secret = appConfig.get("OAUTH2_CLIENT_SECRET"),
                    api_base_url='https://www.googleapis.com/',
                    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo', 
                client_kwargs={ "scope" : "openid email profile"},
                server_metadata_url= 'https://accounts.google.com/.well-known/openid-configuration',
                jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
                )

ser = Serializer(app.config['SECRET_KEY']) 

#Database Tables Updates
def createall(db):
    db.create_all()

#Password Encryption
encrypt_password = Bcrypt()


#Populating variables across all routes
@app.context_processor
def inject_ser():

    return dict(ser=ser)


@app.route("/", methods=['POST','GET'])
def home():

    images=None
    layout = None
    db.create_all()
    al = request.args.get("al")
    cat = request.args.get("cat")
    chck_len=True

    if cat:
        images = Images.query.filter_by(image_category=cat).all()
    elif al:
        images = Images.query.all()
    else:
        images = Images.query.all()

    categories= {app.image_category for app in Images.query.all()}

    if request.args.get('icon'):
        layout = request.args.get('icon')

    return render_template("index.html", images=images, layout=layout, categories=categories,usr_obj=User,chck_len=chck_len)

@app.route('/download_img', methods=['POST',"GET"])
def download():

    img = request.args.get("img_id")
    print("DEBUG: ", img)
    images = Images.query.filter_by(id=img).first()

    return render_template("download.html", image=images, user=User)

@app.route('/logout')
def log_out():

    logout_user()

    return redirect(url_for('home'))

@app.route('/track_click', methods=['POST'])
def track_click():
    data = request.get_json()
    clicked_link = data.get('clicked_link')
    appnm = data.get('appnm')

    user_agents_str = request.headers.get('User-agent')
    user_data=user_agents.parse(user_agents_str)
    usr_addr=request.remote_addr

    if clicked_link:
        stats = stats_image_dlink(
            app_name=appnm,download_link=clicked_link,user_addr=usr_addr,device=user_data.get_device(),
            browser=user_data.get_browser(),timestamp=datetime.now()
        )

        db.session.add(stats)
        db.session.commit()
        # print(f'User clicked the link: {clicked_link}')
        # print(f'...and Name: {appnm}')
        # You can perform logging, analytics, or any other processing here

    return jsonify(success=True)

@app.route("/about", methods=['POST','GET'])
def about():

    return render_template("about.html")


def send_email(app_info,emails=None):
    
    def send_veri_mail():

        app.config["MAIL_SERVER"] = "smtp.googlemail.com"
        app.config["MAIL_PORT"] = 587
        app.config["MAIL_USE_TLS"] = True
        # Creditentials saved in environmental variables
        em = app.config["MAIL_USERNAME"] ='pro.dignitron@gmail.com' # os.getenv("MAIL")  creds.get('email')
        pwd = app.config["MAIL_PASSWORD"] = creds.get('gpass') # os.getenv("PWD")
        app.config["MAIL_DEFAULT_SENDER"] = "thabo@techxolutions.com"

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
        
        msg = Message(subject="Promote Your Mobile App", sender="thabo@techxolutions.com", recipients=["thabo@techxolutions.com",emails])

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

                <div style="color:rgb(53, 53, 53)" class="content"> We believe that your app <span class="bolden"> {app_info.name} </span>significantly contributes to the needs of Eswatini
                    community and would like to feature it prominently on our centralized platform. Many Mobile Apps developed locally take some time to get recognition across the whole community of EmaSwati.
    
                    This platform serve as a repository where users can easily discover and explore mobile applications 
                    that cater to their service requirements. 
                </div>
                
                <!-- Link  -->
                <div style="margin:20px auto;width:max-content"><span>Please Visit TechConnect Plus here:</span><a href="https://prelaunch.techxolutions.com" target="_blank"><span style="background-color: #00a550;color:white;padding:5px 10px;border-radius: 15px;font-weight: 600;font-size: 16px;" class="sub-titles">website</span></div></a>
                <br>
                <div style="width:60%;margin:10px auto" class="content objectives">
                    <!-- Sub Topic  -->
                    <h2 style="color:coral">Key Objects of the Project</h2>
                    <p style="vertical-align: top;"><span><img style="height:20px" src="https://techxolutions.com/images/tick-icon.png" /></span>
                        <span style="" class="bolden">Increased Awareness:</span><span >Our goal is to promote awareness among EmaSwati about diverse mobile applications, encouraging user engagement with these essential digital solutions.
                        </span></p>
                    <p><span><img style="height:20px" src="https://techxolutions.com/images/tick-icon.png" /></span>
                        <span class="bolden">Centralized Hub:</span> <span>Users will have streamlined access to a variety of apps, making it easy for them to locate the resources they need.<br>
                        <span style="color:blue"><a href="{url_for('about',  _external=True)}"> ...read more</a></span>
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
                <p style="font-weight:500;font-size:13px"><span style="font-weight:400"><span style="color:blue"><a href="{url_for('app_form',  _external=True)}"> Publising </a></span> Your App with TechConnectPlus is Free of Charge</span></p>
                <p style="font-weight:500;font-size:13px"><span style="font-weight:400"><span style="color:blue">App Access Code in TechConnect+: </span> {app_info.app_code}</span></p>
                
                </div><br><br>


                <p  class="">Kind Regards,</p> 
                <table style="font-size: medium;background-color: #f1f1f1;width:100% !important;background-color: #f7f6f6;border-radius: 20px;padding:15px" class="email-sign-cont ">
                    <tr style="font-size: medium;width:100% !important" >
                        <td style="vertical-align: top;" class="sign-column">
                            <span style="font-size: large;font-weight: 600;color:#606060">Thabo Maziya</span>
                            <span style="font-size: large;font-weight: 600;color:#606060"></span>
                            <div class="mail-links"><img style="height:25px" src="http://techxolutions.com/images/email_icon.png"/><span>thabo@techxolutions.com</span></div>
                            <div class="mail-links"><img style="height:25px" src="http://techxolutions.com/images/telephone_icon.png"/><span>(+268) 7641 2255</span></div>
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
            emails = email_form.emails.data

        if app_name_rq:
            send_email(app_name_rq,emails=emails)
        else:
            return jsonify({"Error":f"App Name {app_name} Does Not Exists in the System"})

    return render_template("send_email.html",email_form=email_form)


@app.route("/image_form", methods=['POST','GET'])
@login_required
def image_form():

    app_form = ImagesForm()

    if request.method == "POST":

        image_info = Images(
            img_name=app_form.name.data.strip(),description=app_form.description.data.strip(),
            image_category=app_form.image_category.data,timestamp=datetime.now(),uid=current_user.id
            )

        if app_form.image.data:
            image_info.image_thumbnail = process_file(app_form.image.data,current_user)

        db.session.add(image_info)
        db.session.commit()

        flash("Upload was Successful👍","success")

    return render_template("image_form.html",app_form=app_form)


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

# Create a custom Jinja2 filter to remove special characters
@app.template_filter('remove_special_chars')
def remove_special_chars(s):
    return re.sub(r'[^a-zA-Z0-9\s]', '', s)

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
        if app_form_update.edited_by.data:
            app_info.edited_by=app_form_update.edited_by.data

        app_info.publish = app_form_update.publish.data
        app_info.edited = datetime.now()

        if app_form_update.app_icon.data:
            # print("Check if there is data:",app_form_update.app_icon.data )
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


@app.route("/signup", methods=["POST","GET"])
def sign_up():

    register = Register()
    user = None

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':

        if register.validate_on_submit():    

            hashd_pwd = encrypt_password.generate_password_hash(register.password.data).decode('utf-8')

            user = gen_user(
                    name=register.name.data, email=register.email.data, password=hashd_pwd,
                    confirm_password=hashd_pwd,image="default.png"
                    )

            if not Register().validate_email(register.email.data):
                db.session.add(user)
                db.session.commit()
                print('Sign up successful!')
                flash(f"Account Successfully Created for {register.name.data}", "success")
            else:
                flash(f"Something went wrong, check for errors", "error")
                print('Sign up unsuccessful')

            return redirect(url_for('login'))

        elif register.errors:
            flash(f"Account Creation Unsuccessful ", "error")
            print(register.errors)

    # from myproject.models import user
    return render_template("signup_form.html",register=register)

# User Account
@app.route("/user_account", methods=["POST", "GET"])
def user_account():

    usr_account=gen_user.query.get(current_user.id)
    account_form = Register(obj=usr_account)

    if account_form.validate_on_submit():

        if request.method == 'POST':

            usr_account.contacts=account_form.contacts.data
            usr_account.town=account_form.town.data
            usr_account.address=account_form.address.data
            
            if account_form.image.data:
                usr_account.image = process_file(account_form.image.data)

            # try:
            db.session.commit()
            flash(f"Update Successful!", "success")
            print("Update Successful!")


    return render_template('user_account.html',account_form =account_form, usr_account=usr_account)

#Verification Pending
@app.route("/login", methods=["POST","GET"])
def login():

    login = Login()

    if login.validate_on_submit():

        if request.method == 'POST':

            user_login = User.query.filter_by(email=login.email.data).first()
            if user_login and encrypt_password.check_password_hash(user_login.password, login.password.data):

                # if not user_login.verified:
                #     login_user(user_login)
                #     return redirect(url_for('verification'))
                # else:
                # After login required prompt, take me to the page I requested earlier
                # login_user(user_login)
                # print("No Verification Needed: ", user_login.verified)

                # Check If are they allocated to a church 

                login_user(user_login)
                flash(f"Hey! {user_login.name.title()} You're Logged In!", "success")

                req_page = request.args.get('next')
                return redirect(req_page) if req_page else redirect(url_for('home'))
                
            else:
                flash(f"Login Unsuccessful, please use correct email or password", "error")
                # print(login.errors)
    else:
        print("No Validation")
        if login.errors:
            for error in login.errors:
                print("Errors: ", error)
        else:
            print("No Errors found", login.email.data, login.password.data)

    return render_template("login.html",login=login)


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


@app.route("/google_signup", methods=["POST","GET"])
def google_signup():

    return render_template('google_signup.html')

#google login
@app.route("/google_login", methods=["POST","GET"])
def google_login():

    # print("DEBUG CREDITENTAILS: ",appConfig.get("OAUTH2_CLIENT_ID"),' ',appConfig.get("OAUTH2_CLIENT_SECRET"))

    return oauth.appenda_oauth.authorize_redirect(redirect_uri=url_for("google_signin",_external=True))


#login redirect
@app.route("/google_signin", methods=["POST","GET"])
def google_signin():

    token = oauth.appenda_oauth.authorize_access_token()

    session['user'] = token

    pretty=session.get("user")

    usr_info = pretty.get('userinfo')
    verified = usr_info.get("email_verified")
    usr_email = usr_info.get("email")
    usr_name=usr_info.get("name")
    usr_athash=usr_info.get("at_hash")

    if not verified:
        flash("Access Denied!, Your Email is not verified with Google")
        flash("Please, Set up your account manually")
        return redirect(url_for('sign_up'))
    
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    #Sign Up
    if not User.query.filter_by(email=usr_email).first():

        print("Email Not Found!, We will register")

        # context
        hashd_pwd = encrypt_password.generate_password_hash(usr_athash).decode('utf-8')
        user1 = gen_user(name=usr_name, email=usr_email, password=hashd_pwd,
                        confirm_password=hashd_pwd, image="default.jpg",timestamp=datetime.now(),verified=True)

        try:
            db.session.add(user1)
            db.session.commit()

            #Login user
            usr_obj = User.query.filter_by(email=usr_email).first()
            #Check if user have a church id
            if usr_obj.chrch_id:
                login_user(usr_obj)
            else:
                return redirect(url_for('select_church'))

            # if not current_user.church_local and not current_user.church_zone:
            #     return redirect(url_for('finish_signup'))
        
        except IntegrityError:
            db.session.rollback()  # Rollback the session on error
            return jsonify({"message": "Email already exists"}), 409
        
        except Exception as e:
                db.session.rollback()  # Rollback on any other error
                return jsonify({"message": "An error occurred", "error": str(e)}), 500
        
    else:
        user_login = User.query.filter_by(email=usr_email).first()

        if not user_login.verified:
            login_user(user_login)
            return redirect(url_for('verification'))

        if user_login.chrch_id:
            login_user(user_login)
            flash(f"Hey! {user_login.name.title()} You're Logged In!", "success")
            if user_login.role == "gen_user":
                user = gen_user.query.get(user_login.id)
                if not user.gender or not user.contacts or not user.address:
                        print(user.gender ,user.contacts, user.address)
                        return redirect(url_for('usr_finish_signup'))
            else:
                user = admin_user.query.get(user_login.id)
                if not user.gender or not user.contacts or not user.address:
                    return redirect(url_for('admin_finish_signup'))
            _activity(user_login)
        else:
            flash(f"Please Select Your Local Church", "success")
            login_user(user_login)
            return redirect(url_for('select_church'))

        req_page = request.args.get('next')
        return redirect(req_page) if req_page else redirect(url_for('home'))
    

    return redirect(url_for("home"))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


