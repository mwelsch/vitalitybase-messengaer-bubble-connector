import time



def log(text):
    file1 = open("log", "a")  # append mode
    file1.write("\n")
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    current_time += text
    file1.write(current_time)
    file1.close()
