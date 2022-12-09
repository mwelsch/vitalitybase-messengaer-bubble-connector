def get_whitelist_members():
    f = open("whitelist", "r")
    lines = f.readlines()
    members = []
    for line in lines:
        line = line.replace("\n", "")
        members.append(line)
    return members