def get_nick(full_name):
    return full_name.split('!', 1)[0]

def get_host(full_name):
    return str(full_name).strip().split('@', 1)[1]

