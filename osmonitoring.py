import psutil
import time
import mysql.connector
from mysql.connector import errorcode


def fixed(numObj, digits=2):
    return f"{numObj:.{digits}f}"


def convert_to_preferred_format(total):
    days = total // (3600*24)
    sec = total % 60
    hour = (total // 3600) % 24
    minutes = (total // 60) % 60
    return "%02d:%02d:%02d:%02d" % (days, hour, minutes, sec)


def get_data():
    cpu = psutil.cpu_percent(interval=None)
    mem = fixed(psutil.virtual_memory().used / (1024.0 ** 3))
    hdd = psutil.disk_usage('/').percent
    user_list = psutil.users()
    user_info = ''
    count = 0
    for user in user_list:
        user_info += psutil.users()[count][0]
        user_info += ' '
        count += 1
    current_time = time.time()
    boot_time = psutil.boot_time()
    timedelta = current_time - boot_time
    timework = convert_to_preferred_format(timedelta)
    global os_date
    os_date = []
    os_date.append(str(cpu)), os_date.append(mem), os_date.append(str(hdd)), \
    os_date.append(user_info), os_date.append(timework)


def main():
    username = input("Enter MySQL user: ")
    userpassword = input("Enter user's password: ")
    dbhost = input("Enter MySQL DB IP: ")
    userdb = input("Enter DB name: ")
    try:
        cnx = mysql.connector.connect(user=username, password=userpassword,
                                      host=dbhost, database=userdb)
        curA = cnx.cursor(buffered=True)
        curB = cnx.cursor(buffered=True)
        curC = cnx.cursor(buffered=True)
        loop = True
        while loop:
            try:
                curA.execute("SELECT * FROM date_os")
                get_data()
                curA.execute(
                    "UPDATE date_os SET id = %s, CPU = %s, RAM = %s, HDD = %s, Users = %s, WorkTime = %s WHERE ID = %s ",
                    (1, os_date[0], os_date[1], os_date[2], os_date[3], os_date[4], 1))
                cnx.commit()
                time.sleep(30)
            except:
                create_osdate_query = """
                                 CREATE TABLE date_os(
                                     id INT AUTO_INCREMENT PRIMARY KEY,
                                     CPU TEXT NOT NULL,
                                     RAM TEXT NOT NULL,
                                     HDD TEXT NOT NULL,
                                     Users TEXT NOT NULL,
                                     WorkTime TEXT NOT NULL
                                 )
                                 """
                curB.execute(create_osdate_query)
                insert_values = "insert into date_os(id, CPU, RAM, HDD, Users, WorkTime) values(%s, %s, %s, %s, %s, %s)"
                values = (0, "No", "No", "No", "No", "No")
                curC.execute(insert_values, values)
                cnx.commit()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cnx.close()


if __name__ == "__main__":
    main()
