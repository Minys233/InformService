import smtplib
from email.message import EmailMessage
from email import encoders
from email.header import Header
from email.utils import formataddr, parseaddr

from InformService.utils import make_logger
from InformService.credential import load_credential, create_credential

logger = make_logger(__name__)

class EmailSender:
    def __init__(self, record_name=None, SSL=True, sender_name='土木的机器人', **kwargs):
        if record_name is None:
            self.record = create_credential()
        else:
            self.record = load_credential(record_name)
        logger.info(f"{record_name} loaded.")
        if SSL:
            self.server = smtplib.SMTP_SSL(host=self.record['Host'])
        else:
            self.server = smtplib.SMTP(host=self.record['Host'])
        self.server.login(self.record['Address'], self.record['Password'])
        logger.info("Logged in successfully.")
        self.msg = EmailMessage()
        self.setcontent(sender_name=sender_name, **kwargs)

    def setcontent(self, sender_name, **kwargs):

        if 'Content' in kwargs:
            self.msg.set_content(kwargs['Content'])
        else:
            self.msg.set_content("测试邮件喵，🐱！")

        if 'Subject' in kwargs:
            self.msg['Subject'] = "[Yaosen-Information-Service]  " + kwargs['Subject']
        else:
            self.msg['Subject'] = "[Yaosen-Information-Service] 测试邮件"

        if 'To' in kwargs:
            self.msg['To'] = kwargs['To']
        else:
            self.msg['To'] = self.record['Address']

        self.msg['From'] = formataddr((sender_name, self.record['Address']), 'UTF-8')




        # fuck, from line should be put behind set_content or email will not display properly
        # To line should be in front of from line, or receiver will be displayed empty
        # this must be a bug



    def send(self):
        self.server.send_message(self.msg)
        self.server.quit()


if __name__ == '__main__':
    # print(formataddr((str(Header('机器人', 'utf-8')), 'from@mywebsite.com')))
    sender = EmailSender('minys18')
    sender.send()
