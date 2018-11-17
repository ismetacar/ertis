from flask_mail import Message


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    return msg


#: Usage
#: app.mail.send(send_email(
#:     "ertis test denemesi",
#:     settings["mail_username"],
#:     recipients=["dismetacar@gmail.com", "muratcemcem@gmail.com"],
#:     text_body="ertis akar hacı",
#:     html_body=render_template('email_template.html')
#: ))
