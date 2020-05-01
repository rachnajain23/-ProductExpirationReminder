import sqlite3
import enum

class NotifyMode(enum.Enum):
    email = 1
    phone = 2

conn = sqlite3.connect('product_expiration.db')
print ("Opened database successfully");

# # conn.execute('''DROP TABLE Product;''')
# conn.execute('''DROP TABLE User;''')
# conn.execute('''DROP TABLE User_Product;''')

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
          product_name VARCHAR NOT NULL,
          mfg_date TEXT NOT NULL,
          expiry_date TEXT NOT NULL,
          notify_date VARCHAR NOT NULL,
          FOREIGN KEY(user_id) REFERENCES User(user_id)

         )
         ;''')

conn.commit()
conn.close()

print ("Tables created successfully");
