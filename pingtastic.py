#!/usr/bin/env python

import smtplib
from email.mime.text import MIMEText
import sys
import requests
import time

URL_FILE = 'urls.conf'


class Problem(object):
    """
    Wrapper around a failed request.
    """

    def __init__(self, url, elapsed_time, response=None, exception=None):
        self.url = url
        self.elapsed_time = elapsed_time
        if response is not None:
            self.explanation = "Status code %s" % response.status_code
        elif exception is not None:
            self.explanation = "Exception %s" % str(exception)
        else:
            raise Exception("Missing response and exception")


    def __str__(self):
        return "%s failed because of %s after %s seconds" % (self.url,
                                                             self.explanation,
                                                             self.elapsed_time )

def notify(user, pw, email, problems):
    """
    Send an email to the specified address with results.
    """

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    FROM_EMAIL = user

    # Create a text/plain message
    msg = MIMEText("\n".join([str(p) for p in problems]))
    msg['Subject'] = 'There were %d problems' % len(problems)
    msg['From'] = FROM_EMAIL
    msg['To'] = email

    mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    mail.starttls()
    mail.login(user, pw)
    mail.sendmail(FROM_EMAIL, [email], msg.as_string())

    mail.quit()

# Script
if __name__ == '__main__':
    try:
        EMAIL = sys.argv[1]
    except:
        sys.stderr.write("Missing email (arg 1).")
        sys.exit(1)

    try:
        USER = sys.argv[2]
    except:
        sys.stderr.write("Missing user (arg 2).")
        sys.exit(1)

    try:
        PW = sys.argv[3]
    except:
        sys.stderr.write("Missing pw (arg 3).")
        sys.exit(1)

    try:
        urls = open(URL_FILE, 'r')
    except IOError as e:
        sys.stderr.write("Couldn't open %s: %s" % ( URL_FILE, e ))
        sys.exit(1)

    errs = []

    for url in urls:
        url = url.rstrip()
        (response, exception) = (None, None)
        try:
            start_time = time.time()
            response = requests.get(url)
            elapsed_time = time.time() - start_time
            if response.status_code != 200 or elapsed_time > 3:
                errs.append(Problem(url, elapsed_time, response=response))
        except Exception as e:
            elapsed_time = time.time() - start_time
            errs.append(Problem(url, elapsed_time, exception=e))

    if len(errs):
        try:
            notify(USER, PW, EMAIL, errs)
        except Exception as e:
            sys.stderr.write("Couldn't send email: %s" % e)

