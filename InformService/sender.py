import smtplib
from email.message import EmailMessage
from email.utils import formataddr
import mimetypes

from InformService.utils import make_logger
from InformService.credential import load_credential, create_credential
import InformService.config

logger = make_logger(__name__)
"""
TODO: 
1. Multi-recipient feature. Now only one recipient are allowed.
2. Other content type. Now email content is plain text only, may be html or template system is better?

"""

DEFAULT_SUBJECT = InformService.config.DEFAULT_SUBJECT
DEFAULT_SUBJECT_PREFIX = InformService.config.DEFAULT_SUBJECT_PREFIX
DEFAULT_CONTENT = InformService.config.DEFAULT_CONTENT


def change_default_subject_prefix(s: str):
    global DEFAULT_SUBJECT_PREFIX
    DEFAULT_SUBJECT_PREFIX = s + '  '


def change_default_subject(s: str):
    global DEFAULT_SUBJECT
    DEFAULT_SUBJECT = s


def change_default_content(s: str):
    global DEFAULT_CONTENT
    DEFAULT_CONTENT = s

class EmailSender:
    def __init__(self, record_name=None, SSL=True, sender_name='InformServiceBot', reciever_name="", **kwargs):
        if record_name is None:
            self.record = create_credential()
        else:
            self.record = load_credential(record_name)
        logger.info(f"Credential {record_name} loaded.")
        if SSL:
            self.server = smtplib.SMTP_SSL(host=self.record['Host'])
        else:
            self.server = smtplib.SMTP(host=self.record['Host'])
        self.server.login(self.record['Address'], self.record['Password'])
        logger.info("Logged in successfully.")
        self.msg = EmailMessage()
        self.setcontent(sender_name=sender_name, reciever_name=reciever_name, **kwargs)

    def setcontent(self, sender_name, reciever_name, **kwargs):
        logger.info(f"Sender {self.record['Address']} with display name '{sender_name}'.")
        self.msg['From'] = formataddr((sender_name, self.record['Address']), 'utf-8')

        # Now only one recipient is accepted
        # If no 'To' keyword are specified, EmailSender assumes send email to sender's mailbox
        if 'To' in kwargs:
            logger.info(f"Send email to {kwargs['To']} with display name '{reciever_name}'.")
            self.msg['To'] = formataddr((reciever_name, kwargs['To']), 'utf-8')
        else:
            logger.info(f"No recipient specified, "
                        f"send email to sender {self.record['Address']} with display name '{reciever_name}'.")
            self.msg['To'] = formataddr((reciever_name, self.record['Address']), 'utf-8')

        self.msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'

        # Content could use python string and could be processed normally
        if 'Content' in kwargs:

            self.msg.set_content(kwargs['Content'])
        else:
            self.msg.set_content(DEFAULT_CONTENT)

        # Subject could use python string and could be processed normally
        if 'Subject' in kwargs:
            self.msg['Subject'] = DEFAULT_SUBJECT + kwargs['Subject']
        else:
            self.msg['Subject'] = DEFAULT_SUBJECT_PREFIX + DEFAULT_SUBJECT

        if 'Files' in kwargs:
            for fname in kwargs['Files']:
                ctype, encoding = mimetypes.guess_type(fname)
                if ctype is None or encoding is not None:
                    ctype = "application/octet-stream"
                maintype, subtype = ctype.split('/', 1)
                filename = fname.split('/')[-1]
                with open(fname, 'rb') as fp:
                    self.msg.add_attachment(fp.read(), maintype=maintype, subtype=subtype, filename=filename)

    def send(self):
        # https://stackoverflow.com/questions/43086244/send-e-mail-from-python-with-umlaut-in-the-in-recipients-or-senders-name
        # server.send_message The problem is that send_message tries to
        # use the content of the To and From headers to build the enveloppe
        # addresses but unfortunately it is broken for addresses containing
        # non ASCII characters even if they are in the name part.
        self.server.sendmail(self.msg["From"], self.msg["To"], self.msg.as_string())
        self.server.quit()


if __name__ == '__main__':
    change_default_subject_prefix("🤪")
    change_default_subject("It works!")
    change_default_content("🥳🥳🥳")
    sender = EmailSender('minys18', sender_name="发件人📧", reciever_name="收件人📧", Files=["./LICENSE", '.gitignore'])
    # print(sender.msg.as_string(unixfrom=True))
    sender.send()