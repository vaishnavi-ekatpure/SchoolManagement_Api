from flask_mail import Mail
import os

mail = Mail()

def configure_mail(app):
    app.config['MAIL_SERVER']= os.getenv('EMAIL_HOST')
    app.config['MAIL_PORT'] = os.getenv('EMAIL_PORT')
    app.config['MAIL_USERNAME'] = os.getenv('EMAIL_HOST_USER')
    app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_HOST_PASSWORD')
    app.config['MAIL_USE_TLS'] = os.getenv('EMAIL_USE_TLS')

    mail.init_app(app)