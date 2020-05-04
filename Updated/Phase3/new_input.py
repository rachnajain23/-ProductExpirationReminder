import re
import services
import imageRecognition
import exnew
from datetime import date, datetime, timedelta
from flask import Flask, render_template ,request, url_for,flash,jsonify, session ,escape
from werkzeug.utils import secure_filename
import pytesseract
import os
import numpy as np

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
# app.secret_key='dont tell anyone'
app.config['UPLOAD_FOLDER'] = 'Images'
app.secret_key = "jhjdgshaklkjfd"

@app.route('/register', methods=['POST'])
def register():
    name = request.form['usernamesignup']
    email = request.form['emailsignup']
    password = request.form['passwordsignup']
    phno = request.form['phonesignup']
    notifymode = request.form['r']
    success = services.registerLogin(name, email, password, phno, notifymode)
    if (success == True):
        flash("Successfully registered.")
        return render_template('firstpage.html')
    else:
        flash("User Already Exists with this Email, Login.")
        return render_template('firstpage.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['username']
    user_password = request.form['password']
    status = services.login(email, user_password)
    if (status == True):
        session['username'] = email
        if(check()):
            return render_template('addOrView.html', username=session['username'])
    else:
        flash("Invalid email or password")
        return render_template('firstpage.html')

@app.route('/logout')
def logout():
    if(check() == False):
        flash("You've already logged out")
        return render_template('firstpage.html')
    session.pop('username', None)
    return render_template('firstpage.html')

def check():
   if 'username' in session:
     username = session['username']
     return True
   return False

@app.route("/additem",methods=["POST"])
def add_item():
    product_name = request.form['pname']
    reminder_num = request.form['nor']
    mode = request.form['mode']
    if mode == "manually":
        return render_template('Manual.html',pname=product_name,nor=reminder_num)
    else:
        return render_template('uploadImage.html',pname=product_name,nor=reminder_num)

@app.route("/addimage/<pname>/<nor>",methods=['GET', 'POST'])
def add_image(pname,nor):
    if request.method == 'POST':
        if('file' not in request.files):
            flash("Please upload the image.")
            return render_template('uploadImage.html',pname=pname,nor=nor)
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if(check()):
                username = session['username']
            filename = filename.split(".")[0] + "_" + username + "." + filename.split(".")[1]
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            currDate = date.today()
            list = imageRecognition.imagedetection(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            if(os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'],filename))):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'],filename))

            exp_date = None
            if list[2] == 0:
                mfg_date = currDate
                duration = exnew.predict_exp(product_name)
                if not np.isnan(duration):
                    exp_date = mfg_date + timedelta(days=duration)
            else:
                if list[0] == None:
                    print("sorry we couldn't find your product. Enter manually")
                    flash("Sorry couldn't find your product. Enter manually")
                    return render_template('Manual.html', pname=pname, nor=nor)
                elif list[1] == None:
                    mfg_date = list[0]
                    duration = exnew.predict_exp(pname)
                    if not np.isnan(duration):
                        exp_date = mfg_date + timedelta(days=duration)
                else:
                    mfg_date = list[0]
                    exp_date = list[1]

            if(exp_date!=None):
                isProdExpired = False
                if (exp_date < currDate):
                    print("Product already Expired!")
                    isProdExpired = True
                    flash("Product already expired!")
                    return render_template('uploadImage.html',pname=pname,nor=nor)
                elif (exp_date == currDate):
                    print("Product Expires today!")
                    isProdExpired = True
                    flash("Product expires today!")
                    return render_template('uploadImage.html',pname=pname,nor=nor)
                else:
                    services.add_items(session['username'], pname, str(mfg_date), str(exp_date), nor, isProdExpired)
                    flash("Added successfully!")
                    results=services.view_details(username)
                    return render_template('view.html',results=results)
                # return render_template('addOrView.html', username=session['username'])
            else:
                print("Couldn't predict Expiry date. Please enter details manually")
                flash("Sorry couldn't add your product. Enter manually")
                return render_template('Manual.html',pname=pname,nor=nor)

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/view')
def view_details():
    if (check() == False):
        flash("You are logged out. Log in again")
        return render_template('firstpage.html')
    results=services.view_details(session['username'])
    return render_template("view.html",results=results)

@app.route('/delete_item',methods=['GET'])
def delete_item():
    id = request.args.get("unique_id")
    services.delete_items(id)
    print("item delted succesfully")
    return jsonify(status="success")

@app.route('/gotoHome')
def gotoHome():
    return render_template("addOrView.html",username=session['username'])

@app.route('/add')
def add():
    if (check() == False):
        flash("You are logged out. Log in again")
        return render_template('firstpage.html')
    return render_template("additem.html")

@app.route("/manual/<pname>/<nor>",methods=["POST"])
def manual_form(pname,nor):
    mfg_date = request.form['mfgDate']
    exp_date = request.form['expDate']
    bestBefore = request.form['bestBefore']
    currDate = date.today()
    currDate = datetime.strptime(str(currDate), '%Y-%m-%d').date()
    if(mfg_date==""):
        mfg_date = str(currDate)
    format_str1 = '%Y-%m-%d'
    mfg_date1 = datetime.strptime(mfg_date, format_str1).date()
    exp_date1 = None

    if currDate<mfg_date1:
        flash("Manufacture date of the product can't be greater than today. Enter valid dates")
        return render_template('Manual.html',pname=pname, nor=nor)

    if(exp_date!=""):
        exp_date1=datetime.strptime(exp_date, format_str1).date()
        if mfg_date1>exp_date1:
            flash("Expiry date can't be less than manufacture date. Enter valid dates")
            return render_template('Manual.html', pname=pname, nor=nor)

    if(exp_date=="" and bestBefore==""):
        bb_predicted = exnew.predict_exp(pname)
        if(not np.isnan(bb_predicted)):
            exp_date1 = mfg_date1+timedelta(days=bb_predicted)

    elif(exp_date==""):
        exp_date1 = mfg_date1+timedelta(days=int(bestBefore))

    if(exp_date1!=None):
        isProdExpired = False
        if(exp_date1 < currDate):
            print("Product already Expired!")
            isProdExpired = True
            flash("Product already expired!")
            return render_template('Manual.html', pname=pname, nor=nor)
        elif(exp_date1 == currDate):
            print("Product Expires today!")
            isProdExpired = True
            flash("Product expires today")
            return render_template('Manual.html',pname=pname, nor=nor)
        else:
            services.add_items(session['username'], pname, str(mfg_date1), str(exp_date1), nor, isProdExpired)
            flash("Added successfully!")
            results=services.view_details(session['username'])
            return render_template('view.html',results=results)
    else:
        print("Couldn't predict expiry. Please enter a valid product name.")
        flash("Sorry couldn't add your product manually. Enter valid product name")
        return render_template("additem.html")


@app.route('/')
def main():
    if(check()):
        return render_template('addOrView.html', username=session['username'])
    return render_template('firstpage.html')


if __name__ == "__main__":
    app.run(debug=True)
