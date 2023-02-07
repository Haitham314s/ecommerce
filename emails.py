from dotenv import dotenv_values
from pydantic import BaseModel, EmailStr
from typing import List
from models import User
import jwt

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

config_credentials = dotenv_values(".env")


class EmailSchema(BaseModel):
    email: List[EmailStr]


async def send_email(email: List, instance: User):
    token_data = {
        "id": instance.id,
        "username": instance.username
    }

    token = jwt.encode(token_data, config_credentials["SECRET"])

    template = f"""
    <!DOCTYPE html>
    <html>
        <head>
    
        </head>
        <body>
            <div style="display: flex; align-items: center; justify-content: center; flex-direction: column"
            
            <h3>Account Verification</h3>
            <br>
            
            <p>Thanks for choosing Copy Squad, please click on the button below to verify your account.</p>
            
            <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; background: #0275d8; color: white;" href="http://localhost:9000/users/verification/?token={token}">
            Verify your email
            </a>
            
            <p>Please kindly ignore this email if you did not register for Copy Squad and follow along...</p>
            
            </div>
        </body>
    </html>
    """

    message = Mail(
        from_email="Haitham@stretch.com",
        to_emails=email,
        subject="Copy Squad Account Verification Email",
        html_content=template
    )
    try:
        sg = SendGridAPIClient(config_credentials["SENDGRID_API_KEY"])
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
