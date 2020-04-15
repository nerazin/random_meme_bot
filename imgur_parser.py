import string
import random
import os
import shutil
import requests
import imghdr


destination = './pics/'

if not os.path.exists(destination):
    os.makedirs(destination)

def get_image():
    while True:
        amount = random.randint(5, 7)

        random_symbols = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
                                 for _ in range(amount))

        url = "https://i.imgur.com/" + random_symbols + ".jpg"
        file_name = random_symbols + ".jpg"

        response = requests.get(url, stream=True)

        if response.status_code == 404: continue
        if response.url != url: continue

        path_to_file = destination + file_name

        with open(path_to_file, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

        if imghdr.what(path_to_file) == 'gif': continue

        return path_to_file

        # noneWorking = [0, 503, 4939, 4940, 4941, 12003, 5556, 5082]
        # size = os.path.getsize(destination + line)
        #
        # if size in noneWorking:
        #     print("[-] Invalid: " + str(name))
        #     os.remove(destination + line)
        # else:
        #     print("[+] Valid: " + printsc)
