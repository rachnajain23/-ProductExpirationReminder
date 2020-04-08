# import urllib
# from urllib.request import urlopen
#
# def main():
#     username = 'akshu090199@gmail.com'
#     sender = 'ExpiryRem'
#     hash = '59586c4a6f10d807993aa5bd0edb5996d21e0fa8bd2817f2de2cc3452ccf97c2'
#     numbers = (8919678119)
#     test_flag = 0
#     message = ('Hello, fine')
#     values = {'test'    : test_flag, 'uname'   : username, 'hash'    : hash, 'message' : message, 'from'    : sender, 'selectednums' : numbers }
#     url = 'http://www.txtlocal.com/sendsmspost.php'
#     postdata = urllib.parse.urlencode(values).encode("utf-8")
#     req = urllib.request.urlopen(url, postdata)
#     print ('Attempting to send SMS to '+ sname + ' at ' + snumber + ' on ' + tdate)
#     try:
#         response = urllib.request.urlopen(req)
#         response_url = response.geturl()
#         if response_url==url:
#             print('SMS sent!')
#     except urllib2.URLError:
#         print('Send failed!')
#         # print(e.reason)
#
# if __name__ == "__main__":
#     main()
#
#
# # data = urllib.parse.urlencode(d).encode("utf-8")
# # req = urllib.request.Request(url)
# # with urllib.request.urlopen(req,data=data) as f:
# #     resp = f.read()
# #     print(resp)
#
#
#
#
#
#
#
#
#




# import time
# from time import sleep
# from sinchsms import SinchSMS

# function for sending SMS
# def main():

    # enter all the details
    # get app_key and app_secret by registering
    # a app on sinchSMS
    # number = '9494422722'
    # message = 'Hello Message!!!'
    # app_key = 'f5824c66-6081-4032-9377-6948b7e8a68d'
    # app_secret = 'QwueDFwBHUCpPTgJuZUeHw=='
    #
    # client = SinchSMS(app_key, app_secret)
    # response = client.send_message(number, message)
    # message_id = response['messageId']
    # response = client.check_status(message_id)
    #
    # # keep trying unless the status retured is Successful
    # while response['status'] != 'Successful':
    #     print(response['status'])
    #     time.sleep(1)
    #     response = client.check_status(message_id)
    #
    # print(response['status'])
#
# if __name__ == "__main__":
#     main()






import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def main():
    x = ''' Hello, a test mail '''
    mail_content = x
    sender_address = 'expiryreminder2020@gmail.com'
    sender_pass = '12345iiitb'
    receiver_address = 'akshu090199@gmail.com'
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'A test mail sent by Python. It has an attachment.'   #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')

if __name__ == "__main__":
    main()
