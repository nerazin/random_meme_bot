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
    for _ in range(30):
        amount = random.randint(5, 6)

        random_symbols = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
                                 for _ in range(amount))

        url = "https://i.imgur.com/" + random_symbols + ".jpg"
        file_name = random_symbols + ".jpg"

        response = requests.get(url, stream=True)

        if response.status_code == 404:
            print('404 response')
            continue
        if response.url != url:
            print(f'Redirect from {url} to {response.url}')
            continue

        path_to_file = destination + file_name

        with open(path_to_file, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

        if imghdr.what(path_to_file) == 'gif':
            print('Bad file')
            os.remove(path_to_file)
            continue

        print(f'Made it - {url}')

        return path_to_file

        # noneWorking = [0, 503, 4939, 4940, 4941, 12003, 5556, 5082]
        # size = os.path.getsize(destination + line)
        #
        # if size in noneWorking:
        #     print("[-] Invalid: " + str(name))
        #     os.remove(destination + line)
        # else:
        #     print("[+] Valid: " + printsc)
