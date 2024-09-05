import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

SENDGRID_API_KEY = 'hello'


def send_email(to_email, subject, content):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email('fusioncompany@gmail.com')
    to_email = To(to_email)
    content = Content('text/plain', content)
    mail = Mail(from_email, to_email, subject, content)

    try:
        response = sg.send(mail)
        return response.status_code, response.body
    except Exception as e:
        print(f"Error sending email: {e}")
        return None, str(e)

