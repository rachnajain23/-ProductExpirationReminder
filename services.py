import json
import hashlib
import os
from cryptography.fernet import Fernet
import sqlite3
from datetime import datetime, date, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

connection = sqlite3.connect('product_expiration.db')

# @app.route('/api/login', methods=['POST'])
def login(email, user_password):
    # user_name = request.form['user_name']
    # user_password = request.form['user_password']
    crsr = connection.cursor()
    crsr.execute('SELECT password FROM User WHERE email = ?', [str(email)])
    record = crsr.fetchone()
    password = record
    # print(password)
    # print(str(cipher_suite.decrypt( password[0][0][2:-1].encode() ))[2:-1])
    if password == None or len(password) == 0 or len(password[0]) == 0 or check_password(user_password,password[0]) == False:
        # if password == None or len(password) == 0 or len(password[0]) == 0 or str(cipher_suite.decrypt(password[0][0][2:-1].encode()))[2:-1] != user_password:
        print("failure")
        return

    print("Success")
    return True
    # view_add_details.UserPage(email)
    # return


def set_password(raw_password):
    salt = os.urandom(32)
    #print(salt)
    key = hashlib.pbkdf2_hmac('sha256', raw_password.encode('utf-8'), salt, 100000)
    password = salt + key
    return password


def check_password(raw_password, enc_password):
    salt = enc_password[:32]
    #print(salt)
    key = enc_password[32:]
    #print(key)
    new_key = hashlib.pbkdf2_hmac('sha256', raw_password.encode('utf-8'), salt, 100000)
    #print(new_key)
    return new_key == key


# @app.route('/api/register-login', methods=['POST'])
def registerLogin(name,email,password,phno,notifymode,):
    # user_name = request.form['user_name']

    # print("Information of that face", admin_name)
    # admin_password = request.form['admin_password']
    # print("Information of that face", admin_password)

    ciphered_password = set_password(password)
    # ciphered_password = cipher_suite.encrypt(str(password).encode())
    user_id = connection.execute('INSERT INTO User(email,password,name,phno,notifymode) values(?,?,?,?,?)',(email, ciphered_password, name, phno, notifymode))
    connection.commit()
    #crsr = connection.cursor()
    #crsr.execute("SELECT * FROM User")
    #record = crsr.fetchall()
    #for row in record:
    #   print(row)
    print("Success")
    return

def setReminders(expiryDate_str,reminderNum):
    expiryDate = datetime.strptime(expiryDate_str, '%m-%d-%y').date()
    # print(expiryDate)

    currDate = date.today()
    # print(currDate)

    notifyMap = {'5': 10, '4': 5, '3': 2, '2': 1, '1': 0}
    noofDays = notifyMap[str(reminderNum)]

    notifyDates = ""
    if(currDate+timedelta(days=noofDays) <= expiryDate):   #default
        for i in range(reminderNum):
            notifyDates+=str(expiryDate-timedelta(days=notifyMap[str((reminderNum-i))]))
            notifyDates+=str(" ")
    else:
        if(currDate+timedelta(days=reminderNum) <= expiryDate):
            startNotifyDate = expiryDate-timedelta(days=reminderNum-1)
            print("One notification each day starting from ", startNotifyDate, " till ",expiryDate)
            for i in range(reminderNum):
                notifyDates+=str(startNotifyDate+timedelta(days=i))
                notifyDates+=str(" ")
        else:
            print("One notification everyday and the rest notification on ", expiryDate)
            for i in range(reminderNum):
                if(currDate+timedelta(days=i) < expiryDate):
                    notifyDates+=str(currDate+timedelta(days=i))
                    notifyDates+=str(" ")
                else:
                    notifyDates+=str(expiryDate)
                    notifyDates+=str(" ")

    return notifyDates

def add_items(email, product_name, mfg_date, expiryDate_str, reminderNum):
    notifyDate = setReminders(expiryDate_str,reminderNum)

    # conn = sqlite3.connect('product_expiration.db')
    # print("Opened database successfully")

    user = connection.execute("SELECT user_id FROM User Where email=?", (email,))
    user_id = 1
    product_id = 1
    for row in user:
        # print("User ID: ", row[0])
        user_id = row[0]
    product = connection.execute("SELECT product_id FROM Product Where product_name=?", (product_name,))
    for row in product:
        # print("product ID: ", row[0])
        product_id = row[0]

    connection.execute("INSERT INTO User_Product(user_id,product_id,mfg_date,expiry_date,notify_date) VALUES(?,?,?,?,?)",(user_id, product_id, mfg_date,expiryDate_str,notifyDate))
    connection.commit()
    # connection.close()

def view_details(email):
    # conn = sqlite3.connect('product_expiration.db')
    # print("Opened database successfully")
    cur = connection.cursor()
    user = cur.execute("SELECT user_id FROM User Where email=?", (email,))
    for row in user:
        user_id = row[0]
        # print("User ID: ", row[0])
    print("--------------1-------------------")
    product_Ids = []
    results=[]
    # expiry_Ids=[]
    for row in cur.execute('SELECT product_id,mfg_date,expiry_date FROM User_Product WHERE user_id=?', (user_id,)):
        product_Ids.append(row[0])
        results.append([row[0],row[1],row[2]])
        # expiry_Ids.append(row[2])
    


    for ID in results:
        for row in cur.execute('SELECT * FROM Product WHERE product_id=?', (ID[0],)):
            print("ID:", row[0])
            print("Product Name:", row[1])
            print("Best Before (in days):", row[2])
            print("Category:", row[3])
            print("Manufactured Date:",ID[1])
            print("Expiry Date:",ID[2])

            print("--------------2-------------------")
    # print("--------------3-------------------")
    cur.close()

def sendNotificationMail(msg,email):
    print("Hello, a test mail")
    mail_content = msg
    sender_address = 'expiryreminder2020@gmail.com'
    sender_pass = '12345iiitb'
    receiver_address = email
    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'A test mail sent by Python. It has an attachment.'   #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com') #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')

def sendNotificationPhone(msg,phno):
    print("Notify through phone")
    # TODO

def showNotifyDetails(uname, pname, expDate,notifyMode,email,phno):
    currDate = date.today()
    print(expDate)
    # expiryDate = datetime(*[int(item) for item in (expDate).split('-')]).date()
    print(currDate)
    # expiryDate= datetime.strptime(expDate,'%d-%m-%y').strftime('%Y-%m-%d')
    format_str = '%d-%m-%y'
    expiryDate=datetime.strptime(expDate, format_str).date()
    print(type(currDate))
    print(type(expiryDate))
    print(expiryDate)
    msg = "'''" + "Hey "+uname+", your "+pname+" expires on "+expDate+" which is "+str((expiryDate-currDate).days)+" days from today!" +"'''"
    print(msg)
    if(notifyMode == 1):
        sendNotificationMail(msg,email)
    else:
        sendNotificationPhone(msg,phno)

def getNameFromIds(id,choice):
    if(choice == 'User'):
        # print("Return username")
        for row in connection.execute("Select name from User where user_id = ?",(id,)):
            userName = row[0]
            return userName
    else:
        if(choice == 'Product'):
            # print("Returns productname")
            for row in connection.execute("Select product_name from Product where product_id = ?",(id,)):
                proName = row[0]
                return proName

def notifyUsers():
    # print("Inside Notify USers")
    # connection = sqlite3.connect('product_expiration.db')
    crsr = connection.cursor()
    record=connection.execute("Select up_id, notify_date from User_Product")
    # record=crsr.fetchall()
    for row in record:
        dateList = row[1].split(" ",1)
        dates = dateList[0]
        currDate = str(date.today())
        print(dates)
        print(currDate)
        if(dates == currDate):
            up_id = row[0]
            # print(up_id)
            product_expiry_date=''
            for col in  crsr.execute("Select product_id, user_id, expiry_date from User_Product where up_id = ?",(up_id,)):
                # print(col[0])
                uid=col[1]
                pid =col[0]
                product_expiry_date=col[2]
            for col in crsr.execute("Select name, phno, email, notifymode from User where user_id = ?",(uid,)):
                pname = getNameFromIds(pid,'Product')
                showNotifyDetails(col[0], pname, product_expiry_date,col[3],col[2],col[1])
                restDates = dateList[1]
                connection.execute("UPDATE User_Product SET notify_date = ? WHERE up_id = ?",(restDates,up_id,))
                connection.commit()
        else:
            print("No reminders today!")