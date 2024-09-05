from flask import Flask, request, jsonify
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
sg = SendGridAPIClient(SENDGRID_API_KEY)

def send_invite_email(to_email, invite_link):
    subject = 'You are invited!'
    content = f'Click the following link to join: {invite_link}'
    message = Mail(
        from_email='your-email@example.com',
        to_emails=to_email,
        subject=subject,
        plain_text_content=content
    )
    try:
        response = sg.send(message)
        return response.status_code, response.body
    except Exception as e:
        return str(e), None
def send_password_update_email(to_email):
    subject = 'Password Updated'
    content = 'Your password has been updated successfully.'
    message = Mail(
        from_email='your-email@example.com',
        to_emails=to_email,
        subject=subject,
        plain_text_content=content
    )
    try:
        response = sg.send(message)
        return response.status_code, response.body
    except Exception as e:
        return str(e), None
def send_login_alert_email(to_email):
    subject = 'Login Alert'
    content = 'A new login has been detected for your account.'
    message = Mail(
        from_email='your-email@example.com',
        to_emails=to_email,
        subject=subject,
        plain_text_content=content
    )
    try:
        response = sg.send(message)
        return response.status_code, response.body
    except Exception as e:
        return str(e), None
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    invite_link = "http://example.com/invite"  # Generate a real invite link
    # Assume user creation logic here
    status_code, response_body = send_invite_email(email, invite_link)
    if status_code == 202:
        return jsonify({'message': 'Sign up successful, invitation sent!'}), 201
    else:
        return jsonify({'message': 'Sign up failed, email not sent.'}), 500

@app.route('/update_password', methods=['POST'])
def update_password():
    data = request.json
    email = data.get('email')
    # Assume password update logic here
    status_code, response_body = send_password_update_email(email)
    if status_code == 202:
        return jsonify({'message': 'Password updated, notification sent!'}), 200
    else:
        return jsonify({'message': 'Password update failed, email not sent.'}), 500

@app.route('/login_alert', methods=['POST'])
def login_alert():
    data = request.json
    email = data.get('email')
    # Assume login detection logic here
    status_code, response_body = send_login_alert_email(email)
    if status_code == 202:
        return jsonify({'message': 'Login alert sent!'}), 200
    else:
        return jsonify({'message': 'Login alert failed, email not sent.'}), 500

if __name__ == '__main__':
    app.run(debug=True)