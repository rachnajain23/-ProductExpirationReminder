import hashlib
import os
import sqlite3
from datetime import datetime, date, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



def login(email, user_password):
    connection = sqlite3.connect('product_expiration.db')
    crsr = connection.cursor()
    crsr.execute('SELECT password FROM User WHERE email = ?', [str(email)])
    record = crsr.fetchone()
    password = record
    if password == None or len(password) == 0 or len(password[0]) == 0 or check_password(user_password,password[0]) == False:
        print("failure")
        return

    print("Success")
    return True
    crsr.close()
    connection.close()

def set_password(raw_password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', raw_password.encode('utf-8'), salt, 100000)
    password = salt + key
    return password


def check_password(raw_password, enc_password):
    salt = enc_password[:32]
    key = enc_password[32:]
    new_key = hashlib.pbkdf2_hmac('sha256', raw_password.encode('utf-8'), salt, 100000)
    return new_key == key


def registerLogin(name,email,password,phno,notifymode,):
    connection = sqlite3.connect('product_expiration.db')
    crsr = connection.cursor()
    ciphered_password = set_password(password)
    rowaffected = {}
    user_id = crsr.execute('INSERT or IGNORE INTO User(email,password,name,phno,notifymode) values(?,?,?,?,?)',(email, ciphered_password, name, phno, notifymode))
    connection.commit()
    affected_rows = format(crsr.rowcount)
    # print("--------------------------------------------")
    # print(affected_rows,type(affected_rows))
    #rowaffected = format(connection.rowcount)
    #connection.commit()
    #print("Success")

    if int(affected_rows) == 0:
        # print("false")
        return False
    else:
        # print("True")
        return True
    crsr.close()
    connection.close()


def setReminders(expiryDate_str,reminderNum):
    expiryDate = datetime.strptime(expiryDate_str, '%Y-%m-%d').date()
    currDate = date.today()
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

def add_items(email, product_name, mfg_date, expiryDate_str, reminderNum, isProdExpired):
    connection = sqlite3.connect('product_expiration.db')
    if(isProdExpired==True):
        return
    notifyDate = setReminders(expiryDate_str,int(reminderNum))

    user = connection.execute("SELECT user_id FROM User Where email=?", (email,))
    user_id = 1
    for row in user:
        user_id = row[0]
    connection.execute("INSERT INTO User_Product(user_id,product_name,mfg_date,expiry_date,notify_date) VALUES(?,?,?,?,?)",(user_id, product_name, mfg_date,expiryDate_str,notifyDate))
    connection.commit()
    connection.close()

def view_details(email):
    connection = sqlite3.connect('product_expiration.db')
    cur = connection.cursor()
    user = cur.execute("SELECT user_id FROM User Where email=?", (email,))
    for row in user:
        user_id = row[0]
        results = []
        # expiry_Ids=[]
        for row in cur.execute('SELECT up_id,product_name,mfg_date,expiry_date FROM User_Product  WHERE user_id=?', (user_id,)):
            results.append([row])
    cur.close()
    connection.close()
    return results

def delete_items(id):
    connection = sqlite3.connect('product_expiration.db')
    result=connection.execute('DELETE FROM user_product WHERE up_id = ?', (id,))
    if(result):
        print("query executed")
    else:
        print("query not executed")    
    connection.commit()
    connection.close()
    return 

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
    format_str = '%Y-%m-%d'
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


def notifyUsers():
    connection = sqlite3.connect('product_expiration.db')
    crsr = connection.cursor()
    record=connection.execute("Select up_id, notify_date from User_Product")
    for row in record:
        dateList = row[1].split(" ",1)
        dates = dateList[0]
        currDate = str(date.today())
        print(dates)
        print(currDate)
        if(dates == currDate):
            up_id = row[0]
            product_expiry_date=''
            for col in  crsr.execute("Select product_name, user_id, expiry_date from User_Product where up_id = ?",(up_id,)):
                uid=col[1]
                pname =col[0]
                product_expiry_date=col[2]
            for col in crsr.execute("Select name, phno, email, notifymode from User where user_id = ?",(uid,)):
                showNotifyDetails(col[0], pname, product_expiry_date,col[3],col[2],col[1])
                restDates = dateList[1]
                connection.execute("UPDATE User_Product SET notify_date = ? WHERE up_id = ?",(restDates,up_id,))
                connection.commit()
        else:
            print("No reminders today!")
    crsr.close()
    connection.close()
