import netmiko
import getpass
import sys
import time
import multiprocessing
import threading
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


day=time.strftime('%d')
month=time.strftime('%m')
year=time.strftime('%Y')
today=day+"-"+month+"-"+year
#путь где создавать папки с конфигами
path = "C:/Backup/"

def connect_to_device(line):
     print("Настройка роутера" + ('-') + str(line))
     try:
        net_connect = netmiko.ConnectHandler(device_type='cisco_asa', ip=str(line), username=username, password=password)
        output = net_connect.send_config_set(lines_comm)
        time.sleep(1)
        create_folder(path + str(line))
        filename = 'CiscoASA' + str(line) + '-' + today + ".txt"
        with open(os.path.join(path + str(line), filename), "w+", encoding="utf-8") as f:
            f.write(output)
        time.sleep(1)
        with open("Log.txt", "a") as logfile:
            logfile.write('Configuration file saved for' + str(line) + '\n')
        #time.sleep(1)
        #return output
        #print(output)
        sema.release()
     except:
         print("Ошибка подключения к роутеру" + ('-') + str(line) + ', роутер недоступен\обрывы\не включен SSH')
         with open("Errors.txt", "a") as errorfile:
              errorfile.write("Error connection to router" + ('-') + str(line) + ', router unavailable\many disconnects\SSH turned off' + '\r' + '\n')
         sema.release()



def commands_asa():
     with open ('commands_asa.txt') as f_comm:
          lines_comm = f_comm.read().splitlines()
     print ('Команды из файла Commands ASA.txt')
     print (lines_comm)
     return lines_comm

def ip_addresses_asa():
     with open ('ip_addresses_asa.txt') as f_ip:
          lines_ip = f_ip.read().splitlines()
     print ('Адреса роутеров ASA из файла ipaddresses_asa.txt')
     print (lines_ip)
     return

def create_folder(path):
    if not os.path.exists(path):
     try:
      os.makedirs(path)
     except OSError:
      print ("Creation of the directory %s failed" % path)

def read_message_body(filename):
    with open(filename) as f_filename:
        body_message = f_filename.read()
    print('Команды из файла Commands ASA.txt')
    print(lines_comm)
    print(body_message)
    return body_message

def send_errors_mail():
    msg = MIMEMultipart()
    Emailpassword = "password"
    msg['From'] = "mail@mail.ru"
    msg['To'] = "mail@mail.ru"
    msg['Subject'] = "Backup Config Cisco ASA"
    #msg.attach(MIMEImage(file("som-1.jpg").read()))
    message_body = str(read_message_body('Errors.txt'))
    msg.attach(MIMEText(message_body, 'plain'))
    server = smtplib.SMTP('mail.7flowers.ru: 587')
    server.starttls()
    server.login(msg['From'], Emailpassword)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

if __name__ == '__main__':
    threads = []
    max_threads = 10
    sema = threading.BoundedSemaphore(value=max_threads)

    lines_comm = commands_asa();
    ip_addresses_asa();
    print('Введите данные для учетной записи пользователя :')

    username = input("Username: ")
    password = input("Password: ")
    #password = getpass()

    log_file = open('Log.txt', 'r+')
    log_file.truncate(0)
    log_file.close()

    errors_file = open('Errors.txt', 'r+')
    errors_file.truncate(0)
    errors_file.close()


    start_time = time.time()

    f = open('ip_addresses_asa.txt')
    for line in f:
            sema.acquire()
            line = line.splitlines()
            thread = threading.Thread(target=connect_to_device, args=(line))
            threads.append(thread)
            thread.start()

    time.sleep(10)
    send_errors_mail()
print("--- %s seconds ---" % (time.time() - start_time))