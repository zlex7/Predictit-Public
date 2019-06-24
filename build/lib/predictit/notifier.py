import smtplib
import traceback
import time

# Import the email modules we'll need
from email.mime.text import MIMEText

order_email_template  = """ \
<html>
  <head></head>
  <body>
    <h1>%s</h1>
    <p>
       The contract %s has experienced volatility<br>
       Current Price = %f<br>
       5 Minute Percentage Change = %f<br>
       <br>
       See more info at <a>%s</a>
    </p>
  </body>
</html>
"""

error_email_template = """ \
<html>
  <head></head>
  <body>
    <h1>ERROR</h1>
    <p>
        %s
    </p>
  </body>
</html>
"""

# email_from_addr = "a.wlezien2@gmail.com"
# email_password = "FAKE PASSWORD"

# email_to_addr = "a.wlezien@gmail.com"

class PredictItNotifier(object):

    def __init__(self, from_email, from_email_password, to_emails):
        self.from_email = from_email
        self.from_email_password = from_email_password
        self.to_emails = to_emails

    def send_notification(self, subject, message):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(self.from_email, self.from_email_password)

        for to_email in self.to_emails:
            msg = MIMEText(message, 'html')

            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            server.sendmail(self.from_email, to_email, msg.as_string())
        server.quit()

    def send_order_notification(self, contract, quantity, price):
        self.send_notification("Executed order for %d shares of %s at %dc" % (quantity,contract.long_name,price), "")

    def send_error_notification(self, exception, timestamp):
        print(exception)
        print(timestamp)
        self.send_notification("%s: Exception %s occurred" % (timestamp, exception), error_email_template % exception.__traceback__)
