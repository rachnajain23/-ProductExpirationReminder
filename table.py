import sqlite3
import enum

class NotifyMode(enum.Enum):
    email = 1
    phone = 2

conn = sqlite3.connect('product_expiration.db')
print ("Opened database successfully");

#conn.execute('''DROP TABLE Product;''')
#conn.execute('''DROP TABLE User;''')
#conn.execute('''DROP TABLE User_Product;''')

conn.execute('''CREATE TABLE  IF NOT EXISTS Product
         (product_id INTEGER PRIMARY KEY   AUTOINCREMENT,
         product_name  varchar(255)    NOT NULL,
         best_before   INTEGER     NOT NULL,
         category    varchar(255) CHECK(category IN('Groceries' ,'Medicines','Fruits','Vegetables','Documents','Packed Food')) NOT NULL
           )
          ;''')

conn.execute('''CREATE TABLE IF NOT EXISTS User(
              user_id INTEGER PRIMARY KEY AUTOINCREMENT,
              email VARCHAR(30) NOT NULL  UNIQUE,
              password BLOB NOT NULL ,
              name VARCHAR(30) NOT NULL,
              phno VARCHAR(30),
              notifymode  NotifyMode)
           ;''')

conn.execute('''CREATE TABLE IF NOT EXISTS  User_Product
         (
          up_id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL,
          product_id INTEGER NOT NULL,
          mfg_date TEXT NOT NULL,
          expiry_date TEXT NOT NULL,
          notify_date VARCHAR NOT NULL,
          FOREIGN KEY(user_id) REFERENCES User(user_id),
          FOREIGN KEY(product_id) REFERENCES Product(product_id)

         )
         ;''')

# conn.execute('''INSERT INTO User(email,password,name,phno,notifymode) VALUES('ankitab7185@gmail.com','ramanclasses','ankita','8477992835','');'''
conn.execute('''INSERT INTO Product(product_name,best_before,category) VALUES('Maggi',180,'Packed Food');''' )
conn.execute('''INSERT INTO Product(product_name,best_before,category) VALUES('Apple',3,'Fruits');''' )
conn.execute('''INSERT INTO Product(product_name,best_before,category) VALUES('Oats',180,'Packed Food');''' )
conn.execute('''INSERT INTO Product(product_name,best_before,category) VALUES('Potato',15,'Vegetables');''' )
conn.execute('''INSERT INTO Product(product_name,best_before,category) VALUES('Paracetamol',365,'Medicines');''' )
conn.execute('''INSERT INTO Product(product_name,best_before,category) VALUES('Debit Card',1095,'Documents');''' )

conn.commit()
conn.close()

print ("Tables created successfully");
