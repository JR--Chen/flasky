from flask import current_app, render_template, app
from flask_mail import Message
from . import mail
from . import celery


def send_email(to, subject, template, **kwargs):
    send_async_email.delay(str(to), subject, template, **kwargs)


@celery.task
def send_async_email(to, subject, template, **kwargs):
    msg = Message(current_app.config['FLASKY_MAIL_SUBJECT_PREFIX']+' '+subject,
                  sender=current_app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    with app.app_context():
        mail.send(msg)
