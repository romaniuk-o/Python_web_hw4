import logging
import sys
from pathlib import Path
from shutil import copyfile, move
from threading import Thread
import concurrent.futures


file_list = []
folder_list = []


def scan(path: Path) -> None:
    for el in path.iterdir():
        if el.is_dir():
            logging.info(f'Work in folder {el.name}')
            folder_list.append(el)
            thread_ = Thread(target=scan, args=(Path(el),))
            thread_.start()
        else:
            file_list.append(el)


def copy_file(file_path: Path) -> None:
    ext = file_path.suffix[1:]
    new_path = folder_for_scan / ext.upper()
    try:
        new_path.mkdir(parents=True)
        logging.info(f'New folder name is {ext}')
    except FileExistsError:
        pass
    move(file_path, new_path / file_path.name)


def delete_folders(folder: Path) -> None:
    try:
        folder.rmdir()
        logging.info(f'Folder {folder} deleted')
    except OSError:
        logging.info(f'Folder {folder} is not deleted')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(threadName)s %(message)s')
    folder_for_scan = Path(sys.argv[1])
    thread = Thread(target=scan, args=(Path(folder_for_scan),))
    thread.start()
    thread.join()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(copy_file, file_list)

    if concurrent.futures.as_completed(file_list):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.map(delete_folders, folder_list[::-1])
            
    logging.info('Finish sorting')