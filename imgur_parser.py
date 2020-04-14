import string
import random
import os
import shutil
import requests

noneWorking = [0, 503, 4939, 4940, 4941, 12003, 5556, 5082]


destination = './pics/'

if not os.path.exists(destination):
    os.makedirs(destination)

def get_image():
    while True:
        amount = random.randint(5, 6)  # todo make the same with 7 symbols
        if amount == 6:
            N = 3
            picture = str(
                ''.join(
                    random.choice
                    (string.ascii_uppercase + string.digits + string.ascii_lowercase)
                    for _ in range(N)
                )
            )
            picture2 = str(
                ''.join(
                    random.choice(
                        string.digits + string.ascii_lowercase)
                    for _ in range(N)
                )
            )

            name = picture + picture2

            printsc = "http://i.imgur.com/" + "" + str(picture) + str(picture2) + ".jpg"
            line = str(name) + ".jpg"

        if amount == 5:
            N = 5

            picture = str(''.join(
                random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(N)
                )
            )
            name = picture

            printsc = "http://i.imgur.com/" + "" + str(picture) + ".jpg"
            line = str(name) + ".jpg"

        response = requests.get(printsc, stream=True)

        if response.status_code == 404: continue
        if response.url != printsc: continue

        path_to_file = destination + line

        with open(path_to_file, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

        return path_to_file

        # size = os.path.getsize(destination + line)
        #
        # if size in noneWorking:
        #     print("[-] Invalid: " + str(name))
        #     os.remove(destination + line)
        # else:
        #     print("[+] Valid: " + printsc)
