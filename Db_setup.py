import sqlite3

"""This is a file to set-up a test database for main hikers pack app"""

db_conn = sqlite3.connect("HikeDB.db")
theCursor = db_conn.cursor()

TableName = "Items"

try:
    db_conn.execute("CREATE TABLE " + TableName + "(ID INTEGER PRIMARY KEY "
                    "AUTOINCREMENT NOT NULL, ProductName TEXT NOT NULL, "
                    "Weight INTEGER NOT NULL, Brand TEXT NOT NULL, Name TEXT, "
                    "Category TEXT NOT NULL, Comment TEXT);")  # DATA Types: NULL, INTEGER, TEXT, REAL (floating numbers), BLOB (binary data)
    db_conn.commit()

except sqlite3.OperationalError:
     print("Table could not be created")

db_conn.execute("INSERT INTO  " + TableName + " (ProductName, Weight, Brand, Name, Category, Comment) "
                "VALUES('Hiking pants', '585', 'Fjallräven', 'Vidda Pro', 'Clothes', 'Test Comment')")
db_conn.commit()

db_conn.execute("INSERT INTO  " + TableName + " (ProductName, Weight, Brand, Name, Category, Comment) "
                "VALUES('Wool base-layer shirt, short-sleeve', '170', 'Icebreaker', 'Ms Everyday SS Crewe Awesome', "
                "'Clothes', 'Test Comment 2')")
db_conn.commit()

db_conn.execute("INSERT INTO  " + TableName + " (ProductName, Weight, Brand, Name, Category, Comment) "
                "VALUES('Wool base-layer shirt, long-sleeve', '200', 'Icebreaker', 'Ms Everyday SS Crewe Awesome',"
                "'Clothes', 'Test Comment 3')")
db_conn.commit()


def printDB():
    try:
        result = theCursor.execute("SELECT ID, ProductName, Weight, Brand, Name, Category, Comment FROM Items")

        for row in result:
            print("ID :", row[0])
            print("ProductName :", row[1])
            print("Weight :", row[2])
            print("Brand: ", row[3])
            print("Name: ", row[4])
            print("Category: ", row[5])
            print("Comment: ", row[6])
    except sqlite3.OperationalError:
        print("Could not retrieve data..")

printDB()


# Create table for items and packs
try:
    db_conn.execute("CREATE TABLE ItemPack (ID INTEGER PRIMARY KEY "
                    "AUTOINCREMENT NOT NULL, ProductName TEXT NOT NULL, "
                    "PackName TEXT);")  # DATA Types: NULL, INTEGER, TEXT, REAL (floating numbers), BLOB (binary data)
    db_conn.commit()

except sqlite3.OperationalError:
     print("Table could not be created")


# Create table for packs and travels
try:
    db_conn.execute("CREATE TABLE PackTravel (ID INTEGER PRIMARY KEY "
                    "AUTOINCREMENT NOT NULL, PackName TEXT NOT NULL, "
                    "TravelName TEXT);")  # DATA Types: NULL, INTEGER, TEXT, REAL (floating numbers), BLOB (binary data)
    db_conn.commit()

except sqlite3.OperationalError:
     print("Table could not be created")
