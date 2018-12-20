#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
# Name:       replyToMail.py
# Kommentar:  Generiert eine Antwort auf die Mail mit der UID 13962
#             siehe auch https://stackoverflow.com/a/2189630
# Autor:      Jan Stietenroth, Nov, 2017
# Version:    0.1

import email,os

######## load E-Mail from HDD ##########
# run imapToFile.py first. to get an E-Mail
# or use one of the mails generated with 'generateTestmails.py'
fp=open(os.path.abspath("../InputData/mixed.msg"),"rb")
original = email.message_from_binary_file(fp)
fp.close()


####### remove attachments from original #########
for part in original.walk():
    if (part.get('Content-Disposition')
        and part.get('Content-Disposition').startswith("attachment")):

        part.set_type("text/plain")
        part.set_payload("Attachment removed: %s (%s, %d bytes)"
                         %(part.get_filename(), 
                           part.get_content_type(), 
                           len(part.get_payload(decode=True))))
        del part["Content-Disposition"]
        del part["Content-Transfer-Encoding"]



######## create reply message ##########
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.message import MIMEMessage

new = MIMEMultipart("mixed")
body = MIMEMultipart("alternative")
body.attach( MIMEText("Das ist mein Antwort auf die Email", "plain") )
#body.attach( MIMEText("<html>reply body text</html>", "html") )
new.attach(body)

new["Message-ID"] = email.utils.make_msgid()
new["In-Reply-To"] = original["Message-ID"]
new["References"] = original["Message-ID"]
new["Subject"] = "Re: "+original["Subject"]
new["To"] = original["Reply-To"] or original["From"]
#email.utils.parseaddr(msgFrom)[1]
new["From"] = "me@mysite.com"



########## attach the original message and send it ##########
new.attach( MIMEMessage(original) )

s = smtplib.SMTP()
s.sendmail("me@mysite.com", [new["To"]], new.as_string())
s.quit()

print("Ende")
