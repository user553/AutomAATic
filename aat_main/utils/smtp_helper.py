from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr
from smtplib import SMTP_SSL, SMTPException


class EmailHelper:
    @staticmethod
    def send_email(subject, content, receiver_email, sender_name, sender_email):
        forward_email = '945871257@qq.com'
        message = MIMEText(content, 'html', 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')
        message['From'] = formataddr((sender_name, sender_email))
        message['To'] = receiver_email
        try:
            smtp = SMTP_SSL('smtp.qq.com', 465)
            smtp.login(forward_email, 'uppfznrxulnabbjc')
            smtp.sendmail(forward_email, receiver_email, str(message))
            smtp.quit()
        except SMTPException:
            return 'Fail: Send failed'
