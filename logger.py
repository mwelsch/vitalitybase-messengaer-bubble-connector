
def log(text):
    file1 = open("log", "a")  # append mode
    file1.write(text)
    file1.close()
    