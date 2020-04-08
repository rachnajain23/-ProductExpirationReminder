import sqlite3
import re
import services
from datetime import date, datetime

def add_viewItem(email):
    # ReminderService.notifyUsers()
    choices1 = 3
    # cont = 'c'
    # while cont == 'c':
    while(True):
        choice1 = 0
        print("\nWhat do you want to do? (press the corresponding choice no.) \n")
        print("1. Add Items")
        print("2. View Details")
        print("3. Logout")
        while choice1 <= 0 or choice1 > choices1:
            print(f"\nPlease enter a valid input of choice between 1 and {choices1}")
            choice1 = input()
            try:
                choice1 = int(choice1)
            except ValueError:
                choice1 = 0
            print("OK \n")
            if choice1 == 1:
                print("enter the product name")
                product_name = input()
                print("Enter manufacture date in mm-dd-yy format: ")
                currDate = date.today()
                #print(currDate)
                mfg_date = input()
                format_str = '%Y-%m-%d'
                currDate=datetime.strptime(str(currDate), format_str).date()
                format_str1 = '%m-%d-%y'
                mfg_date1=datetime.strptime(mfg_date, format_str1).date()
                while (not re.match(r"^(0[1-9]|[1-9]|1[012])[-](0[1-9]|[1-9]|[12][0-9]|3[01])[-]\d\d$", mfg_date)) or currDate<mfg_date1:
                   print("Invalid Manufacture Date!")
                   mfg_date = input("Enter manufacture date: ")
                   # format_str1 = '%m-%d-%y'
                   mfg_date1=datetime.strptime(mfg_date, format_str1).date()
                exp_date = input("Enter expiry date in mm-dd-yy format: ")
                # format_str1 = '%m-%d-%y'
                exp_date1=datetime.strptime(exp_date, format_str1).date()
                while (not re.match(r"^(0[1-9]|[1-9]|1[012])[-](0[1-9]|[1-9]|[12][0-9]|3[01])[-]\d\d$", exp_date)) or mfg_date1>exp_date1:
                   print("Invalid Expiry Date !")
                   exp_date = input("Enter expiry date: ")
                   # format_str1 = '%m-%d-%y'
                   exp_date1=datetime.strptime(exp_date, format_str1).date()
                while(1):
                    reminderNum = int(input("Enter no.of reminders for your product : "))
                    if(reminderNum > 5 and reminderNum <= 0):
                        print("You can have 1 to 5 reminders only")
                    else:
                        break
                category = 'Fruits'  # TODO - Have to be predicted
                services.add_items(email, product_name, mfg_date, exp_date, reminderNum, category)
#                 services.add_items(email, product_name, mfg_date, exp_date, reminderNum)
            elif choice1 == 2:
                services.view_details(email)
            elif choice1 == 3:
                exit()
                   
                

        # print("Do you want to add or view items? (press c to continue)")
        # cont = input()

def main():
    connection = sqlite3.connect('product_expiration.db')
    crsr = connection.cursor()

    print("\n\nWelcome to Expiry Date Reminder\n")
    choices = 2
    # cont = 'c'
    # while cont == 'c':
    choice = 0
    print("\nWhat do you want to do? (press the corresponding choice no.) \n")
    print("1. Register")
    print("2. Login")
    while choice <= 0 or choice > choices:
        print(f"\nPlease enter a valid input of choice between 1 and {choices}")
        choice = input()
        try:
            choice = int(choice)
        except ValueError:
            choice = 0
    print("OK \n")
    if choice == 1:
        name = input("Enter name:")
        email = input("Enter email:")
        while not re.match(r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", email):
            print("Invalid Email")
            email = input("Enter email:")
        password = input("Enter password:")
        phno = input("Enter phone Number:")
        while not re.match(r"[789]\d{9}$", str(phno)):
            print("Invalid Phone Number")
            phno = input("Enter phone Number:")
        print("How would you like to be notified?")
        print("1. Email")
        print("2. Text message")
        notifymode = input()
        while not (notifymode in ["1", "2"]):
            print("Invalid choice, Enter valid choice")
            notifymode = input()
        services.registerLogin(name,email,password,phno,notifymode)
        add_viewItem(email)
    elif choice == 2:
        email = input("Enter Email id :")
        user_password = input("Enter user_password:")
        status = services.login(email, user_password)
        if(status == True):
            add_viewItem(email)
        # print("Do you want to continue or logout? (press c to continue and any other input to logout)")
        # cont = input()

if __name__ == "__main__":
    main()
