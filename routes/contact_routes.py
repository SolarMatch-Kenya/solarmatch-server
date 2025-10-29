import os
from flask import request, jsonify, Blueprint
from extensions import mail 
from flask_mail import Message

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['POST'])
def handle_contact_form():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email') # Sender's email
    subject = data.get('subject')
    message_body = data.get('message')

    if not all([name, email, subject, message_body]):
        return jsonify({"error": "Missing required fields"}), 400

    # --- Configure Email ---
    # Get recipient email from environment variables
    # (e.g., set CONTACT_EMAIL=your_email@example.com in your .env)
    recipient_email = os.environ.get('CONTACT_EMAIL')
    if not recipient_email:
         # Log this error properly in a real app
        print("ERROR: CONTACT_EMAIL environment variable not set.")
        return jsonify({"error": "Server configuration error"}), 500

    try:
        msg = Message(
            subject=f"Contact Form: {subject}", # Prepend subject line
            # The sender's email address (so you can reply directly)
            sender=email,
            # email address where you receive the messages
            recipients=[recipient_email],
            # Use MAIL_DEFAULT_SENDER as the 'From' name if desired, but sender controls reply-to
            # reply_to=email # Explicitly set reply-to
        )

        # Format the email body
        msg.body = f"""
        You received a new message from your website contact form:

        Name: {name}
        Email: {email}
        Subject: {subject}

        Message:
        {message_body}
        """

        html_message_body = message_body.replace('\n', '<br>')

        
        msg.html = f"""
        <p>You received a new message from your website contact form:</p>
        <hr>
        <p><b>Name:</b> {name}</p>
        <p><b>Email:</b> <a href="mailto:{email}">{email}</a></p>
        <p><b>Subject:</b> {subject}</p>
        <br>
        <p><b>Message:</b></p>
        <p>{html_message_body}</p>
        <hr>
        """

        mail.send(msg)

        return jsonify({"message": "Message sent successfully!"}), 200

    except Exception as e:
        print(f"Error sending contact email: {e}") # Log the error
        return jsonify({"error": "Failed to send message"}), 500