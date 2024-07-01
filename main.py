import pyodbc
import secrets
import sys
import time
from tabulate import tabulate
from datetime import datetime
import datetime

conn = pyodbc.connect('driver=ODBC Driver 18 for SQL Server;server=cypress.csil.sfu.ca;uid=s_saa164;pwd=ePjQ72fL3GrFan2J;Encrypt=yes;TrustServerCertificate=yes')

cur = conn.cursor()

def login():
    global user_id
    global found

    user_id = input("\nEnter your user ID: ")
    cur.execute("SELECT user_id FROM dbo.user_yelp")
    row = cur.fetchone()
    while row:
        if row[0] == user_id:
            print("\nWelcome!")
            found = "True"
            menu()
            break
        else:
            found = "False"
            row = cur.fetchone()

    if found != "True":
        print("Invalid user ID. Please try again.")
        login()

def menu():
    options = '''
    Choose one of the following options:
    1. Search Business
    2. Search Users
    3. Make Friend
    4. Write Review
    5. Logout
    6. Exit
    '''
    print(options)
    select = input("Enter Menu Option Number Here (1-5): ").strip()
    if (select == '1'):
        searchBusiness()
    elif (select == '2'):
        searchUsers()
    elif (select == '3'):
        makeFriend()
    elif (select == '4'):
        writeReview()
    elif (select == '5'):
        print("\nLogging Out User...")
        print("\n-------------------------------------------")
        time.sleep(1)
        login()
    elif (select == '6'):
        print("\nExiting...\n")
        time.sleep(1)
        sys.exit()
    else:
        print("Invalid Option. Please Try Again.")
        time.sleep(1)
        menu()
    
def searchBusiness():
    print("\nEnter search criteria: ")
    city = input("City Name (press enter to skip): ").strip().lower()
    name = input("Business Name (press enter to skip): ").strip().lower()
    maxStar = input("Max Star (press enter to skip): ").strip()
    minStar = input("Min Star (press enter to skip): ").strip()

    searchList = []
    section = []
    section.append("Name")
    section.append("ID")
    section.append("Address")
    section.append("City")
    section.append("Star")

    cur.execute( 'SELECT * from dbo.business' )
    row = cur.fetchone()
    while row:
        found = 1
        if (name != ""):
            if name not in row[1].lower():
                found = 0
        if (city != ""):
            if city not in row[3].lower():
                print(city in row[3].lower(), city, row[3])
                found = 0
        if (maxStar != ""):
            if (float(maxStar) < row[5]):
                found = 0
        if (minStar != ""):
            if (float(minStar) > row[5]):
                found = 0
        if (found == 1):
            result = []
            result.append(row[1])
            result.append(row[0])
            result.append(row[2])
            result.append(row[3])
            result.append(row[5])
            searchList.append(result)
        row = cur.fetchone()

    if (len(searchList) == 0):
        print("No search results found.")
        time.sleep(1)
        menu()

    searchList.sort()
    searchList.insert(0, section)
    print(tabulate(searchList, headers='firstrow', tablefmt="plain"))
    time.sleep(1)
    menu()

def searchUsers():
    print("\nEnter search criteria: ")
    name = input("Name (press enter to skip): ").strip().lower()
    useful = input("Useful(yes/no) (press enter to skip): ").strip().lower()
    funny = input("Funny(yes/no) (press enter to skip): ").strip()
    cool = input("Cool(yes/no) (press enter to skip): ").strip()
    print("\n")
    searchList = []
    section = []
    section.append("Name")
    section.append("ID")
    section.append("Useful")
    section.append("Funny")
    section.append("Cool")
    section.append("Date")

    cur.execute( 'SELECT * from dbo.user_yelp' )
    row = cur.fetchone()
    while row:
        found = 1
        if (row[4] > 0):
            tempUseful = "yes"
        else:
            tempUseful = "no"
        if (row[5] > 0):
            tempFunny = "yes"
        else:
            tempFunny = "no"
        if (row[6] > 0):
            tempCool = "yes"
        else:
            tempCool = "no"
        
        if (name != ""):
            if name not in row[1].lower():
                found = 0
        if (useful != ""):
            if useful == "yes" and row[4] <= 0:
                tempUseful = ""
                found = 0
            if useful == "no" and row[4] > 0:
                found = 0
        if (funny != ""):
            if funny == "yes" and row[5] <= 0:
                found = 0
            if funny == "no" and row[5] > 0:
                found = 0
        if (cool != ""):
            if cool == "yes" and row[6] <= 0:
                found = 0
            if cool == "no" and row[6] > 0:
                found = 0
        if (found == 1):
            result = []
            result.append(row[1])
            result.append(row[0])
            result.append(tempUseful)
            result.append(tempFunny)
            result.append(tempCool)
            result.append(row[3])
            searchList.append(result)
        row = cur.fetchone()
    if (len(searchList) == 0):
        print("No search results found.")
        time.sleep(1)
        menu()

    searchList.sort()
    searchList.insert(0, section)
    print(tabulate(searchList, headers='firstrow', tablefmt="plain"))
    time.sleep(1)
    menu()

def makeFriend():
    print("\nEnter a User ID: ")
    fID = input("USERID (press enter to skip): ").strip()

    if fID == user_id:
        print("\nCannot create a friendship with yourself.")
        time.sleep(1)
        menu()

    cur.execute( 'SELECT * from dbo.user_yelp' )
    row = cur.fetchone()
    exist = 0
    while row:
        if (row[0] == fID):
            exist = 1
            break
        row = cur.fetchone ()

    if (exist == 0):
        print("No such user id exist.")
        time.sleep(1)
        menu()

    cur.execute( 'SELECT * from dbo.friendship' )
    row = cur.fetchone()
    while row:
        if (row[0] == fID):
            if (row[1] == user_id):
                print("Friendship already exists. Please try again")
                time.sleep(1)
                menu()
        if (row[0] == user_id):
            print("You already have a friendship with someone. Cannot add more")
            time.sleep(1)
            menu()
        row = cur.fetchone ()

    SQLCommand = ("INSERT INTO dbo.friendship(user_id, friend) VALUES (?,?)")  
    Values = [user_id, fID]
    cur.execute(SQLCommand,Values)  
    conn.commit()
    print("Friendship Created!!")
    time.sleep(1)
    menu()

def writeReview():

    print("\nCreating Review: ")
    busID = input("Business ID: ").strip()
    stars = input("Stars(1-5): ").strip()

    cur.execute( 'SELECT business_id from dbo.business' )
    row = cur.fetchone()
    exist = 0
    while row:
        if row[0] == busID:
            exist = 1
            break
        row = cur.fetchone()

    if exist == 0:
        print("No such business exist.")
        time.sleep(1)
        menu()
    
    current_datetime = datetime.datetime.now()
    # Convert the datetime object to a string in the format 'YYYY-MM-DD HH:MI:SS.mmm'
    current_datetime_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    # Generating review_id
    review_id = secrets.token_hex(11)

    SQLCommand = ("INSERT INTO dbo.review(review_id, user_id, business_id, stars, useful, funny, cool, date) VALUES (?,?,?,?,?,?,?,?)")  
    Values = [review_id, user_id, busID, stars, 0, 0, 0, current_datetime_str]
    cur.execute(SQLCommand,Values)  
    conn.commit()
    
    print("\nReview Created!!\n")
    time.sleep(1)
    menu()

login()
conn.close()
