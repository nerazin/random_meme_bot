"""
This need for taking fonts from directory with other directories
to another directory

"""


import os
import shutil


def absolute_file_paths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


class FilesWalker:

    def __init__(self, input_folder, output_folder='fonts'):
        self.folder_name = input_folder
        self.output_folder = output_folder
        self.filelist = []

    def sort_files(self):
        minus = 0
        for idx, file in enumerate(absolute_file_paths(self.folder_name)):
            _, file_extension = os.path.splitext(file)
            if file_extension != '.otf':
                minus += 1
                continue
            idx = idx - minus
            generated_path = os.path.normpath(f'{self.output_folder}/{str(idx) + file_extension}')
            shutil.copy2(file, generated_path)


worker = FilesWalker('./database/fonts_for_bot', output_folder='./database/fonts')
worker.sort_files()
