from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField, TextAreaField,BooleanField, SelectField,DateField, URLField,RadioField,IntegerField
from wtforms.validators import DataRequired,Length,Email, EqualTo, ValidationError,Optional
from flask_login import current_user
from flask_wtf.file import FileField , FileAllowed
# from wtforms.fields.html5 import DateField,DateTimeField


class Register(FlaskForm):

    name = StringField('name', validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('email', validators=[DataRequired(),Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=64)])
    confirm = PasswordField('confirm', validators=[DataRequired(),EqualTo('password'), Length(min=8, max=64)])
    contacts = StringField('Contact(s)', validators=[Length(min=8, max=64)])
    zip_code = StringField('Zip Code / Postal Code', validators=[Length(min=0, max=64)])
    address = StringField('Physical Address', validators=[DataRequired(), Length(min=8, max=100)])
    image_pfl = FileField('Profile Image', validators=[FileAllowed(['jpg','png'])])

    submit = SubmitField('Create Account!')

    def validate_email(self,email):
        from app import db, User,app

        # with db.init_app(app):
        user_email = User.query.filter_by(email = self.email.data).first()
        if user_email:
            return ValidationError(f"Email already registered in this platform")




class App_Info_Form(FlaskForm):

    name = StringField('App Name*', validators=[DataRequired()])
    description = TextAreaField('App Description*', validators=[DataRequired()])
    app_category = SelectField('App Category*',choices=[
        ("Communications & Media", "Communications & Media"),
        ("Finance", "Finance"),
        ("Health", "Health"),
        ("Educational", "Educational"),
        ("Entertainment", "Entertainment"),
        ("Travel & Entertainment", "Travel & Entertainment"),
        ("Lifestyle", "Lifestyle"),
        ("Media", "Media"),
        ("Food", "Food"),
        ("Insurance", "Insurance"),
        ("Fast Food", "Fast Food"),
        ("Techonology", "Techonology"),
        ("Training & Skills", "Training & Skills"),
        ("Faith", "Faith"),
        ("Business", "Business"),
        ("Weather", "Weather"),
        ("Sports & Re-Creational", "Sports & Re-Creational"),
        ("Betting & Casino", "Betting & Casino"),
        ("Natural Resources", "Natural Resources"),
        ("Energy", "Energy"),
        ("News", "News"),
        ("Music", "Music"),
        ("Shopping", "Shopping"),
        ("Online Shopping", "Online Shopping"),
        ("Productivity", "Productivity"),
        ("Social Media", "Social Media"),
        ("Utilities", "Utilities"),
        ("Games", "Games")
    ], validators=[DataRequired()])
    app_category_ed = SelectField('App Category',choices=[
        ("Communications & Media", "Communications & Media"),
        ("Finance", "Finance"),
        ("Health", "Health"),
        ("Educational", "Educational"),
        ("Entertainment", "Entertainment"),
        ("Travel & Entertainment", "Travel & Entertainment"),
        ("Lifestyle", "Lifestyle"),
        ("Media", "Media"),
        ("Techonology", "Techonology"),
        ("Training & Skills", "Training & Skills"),
        ("Faith", "Faith"),
        ("Business", "Business"),
        ("Weather", "Weather"),
        ("Sports & Re-Creational", "Sports & Re-Creational"),
        ("Betting & Casino", "Betting & Casino"),
        ("News", "News"),
        ("Music", "Music"),
        ("Shopping", "Shopping"),
        ("Online Shopping", "Online Shopping"),
        ("Productivity", "Productivity"),
        ("Social Media", "Social Media"),
        ("Utilities", "Utilities"),
        ("Games", "Games")
    ], validators=[Optional()])
    # platform = RadioField('Platform(s)*',choices=[('iOS','iOS'), ('Android','Android'), ('All','All')], validators=[DataRequired()])
    # platform_ed = RadioField('Platform(s)',choices=[('iOS','iOS'), ('Android','Android'), ('All','All')], validators=[Optional()])
    version_number = StringField('Version Number')
    playstore_link = URLField("Playstore Download Link*")
    ios_link = URLField("iOS Download Link")
    uptodown_link = URLField("Uptodown Download Link")
    huawei_link = URLField("Huawei Download Link")
    apkpure_link = URLField("APKPure Download Link")
    facebook_link = URLField("Company Facebook Link")
    whatsapp_link = URLField("Company Whatsapp No.")
    x_link = URLField("X Link (Twitter)")
    linkedin_link = URLField("Company LinkedIn Link")
    youtube_link = URLField("Company YouTube Link")
    web_link=URLField("Company Web Link")
    github_link = StringField('GitHub Link')
    app_icon = FileField('App Icon*')
    publish=BooleanField("Publish App",default=True)
    company_name = StringField('Company Name*', validators=[DataRequired()])
    company_contact = StringField('Contacts', validators=[Optional()])
    company_email = StringField('Email*', validators=[DataRequired()])
    edited_by=StringField('Edited by',validators=[DataRequired()])
    submit=SubmitField('submit')


class SendEmailForm(FlaskForm):

    app_name = StringField('App Name', validators=[Length(max=120)])
    emails = StringField('Emails', validators=[Length(max=120)])
    submit = SubmitField('submit')


class EditAppInfoForm(FlaskForm):

    app_name = StringField('App Name', validators=[Length(max=120)])
    app_code = IntegerField('App Code(Check it in Your Email)', validators=[Length(max=120)])
    submit = SubmitField('submit')


class EntertainerUserForm(FlaskForm):
    company_name = StringField('Company Name', validators=[Length(max=120)])
    company_address = StringField('Company Address', validators=[Length(max=120)])
    payment_options = StringField('Payment Options', validators=[Length(max=100)])
    submit = SubmitField('Submit')


class Login(FlaskForm):
    email = StringField('email', validators=[DataRequired(),Email()])
    password = PasswordField('password', validators=[DataRequired(), Length(min=8, max=64)])
    submit = SubmitField('Login')


class Contact_Form(FlaskForm):

    name = StringField('name')
    email = StringField('email', validators=[DataRequired(),Email()])
    subject = StringField("subject")
    message = TextAreaField("Message",validators=[Length(min=8, max=2000)])
    submit = SubmitField("Send")


class Reset(FlaskForm):

    old_password = PasswordField('old password', validators=[DataRequired(), Length(min=8, max=64)])
    new_password = PasswordField('new password', validators=[DataRequired(), Length(min=8, max=64)])
    confirm_password = PasswordField('confirm password', validators=[DataRequired(), EqualTo('new password'), Length(min=8, max=64)])

    reset = SubmitField('Reset')


class Reset_Request(FlaskForm):

    email = StringField('email', validators=[DataRequired(), Email()])
    reset = SubmitField('Submit')

    # def validate_email(self,email):
    #     user = user.query.filter_by