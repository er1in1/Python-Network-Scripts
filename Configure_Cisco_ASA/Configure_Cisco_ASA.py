import netmiko
import getpass
import sys
import time
import multiprocessing
import threading

def connect_to_device(line):
     print("Настройка роутера" + ('-') + str(line))
     try:
        net_connect = netmiko.ConnectHandler(device_type='cisco_asa', ip=str(line), username=username, password=password)
        output = net_connect.send_config_set(lines_comm)
        with open("Log.txt", "a") as logfile:
            logfile.write(output + '\n')
        #time.sleep(1)
        #return output
        #print(output)
        sema.release()
     except:
         print("Ошибка подключения к роутеру" + ('-') + str(line) + ', роутер недоступен\обрывы\не включен SSH')
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


    start_time = time.time()

    f = open('ip_addresses_asa.txt')
    for line in f:
            sema.acquire()
            line = line.splitlines()
            thread = threading.Thread(target=connect_to_device, args=(line))
            threads.append(thread)
            thread.start()


print("--- %s seconds ---" % (time.time() - start_time))