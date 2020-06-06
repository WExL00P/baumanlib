import os
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

ALL_CONTENT_TYPES = ['text', 'audio', 'document', 'photo', 'sticker', 'video',
                     'video_note', 'voice', 'location', 'contact', 'poll']


def send_email(address, subject, body):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(os.getenv('EMAIL_ADDRESS'), os.getenv('EMAIL_PASSWORD'))

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        server.sendmail(os.getenv('EMAIL_ADDRESS'), address, msg.as_string())
        server.quit()
    except:
        print('Email failed to send.')


def remove_emoji(string):
    emoji_pattern = re.compile('['
                               u'\U0001F600-\U0001F64F'
                               u'\U0001F300-\U0001F5FF'
                               u'\U0001F680-\U0001F6FF'
                               u'\U0001F1E0-\U0001F1FF'
                               ']+', flags=re.UNICODE)

    return emoji_pattern.sub(r'', string)
