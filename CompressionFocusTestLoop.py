import time
import datetime
import logging
import subprocess
import os
import shutil

# --- Parameters for the compression ---
source_dir = 'C:\\Users\\Kip\\Desktop\\source'
target_dir = 'C:\\Users\\Kip\\Desktop\\target'
path_to_caesiumclt_exe = "C:\\Users\\Kip\\Documents\\caesiumclt\\caesiumclt.exe"
# folder_to_watch = "E:\\import_photos"
folder_to_watch = "C:\\Users\\Kip\\Desktop\\target"
compress_existing_images = False  # Compresser ou pas les images existantes
compression_factor = 60  # 0 = Pas de compression, 80 compression commune
wait_time_between_checks = 2  # En secondes, l'écoulement entre chaque check de dossier
# scale_factor = 0.8 # Réduit la résolution en %, 0.1 = -90%, 1.0 = pas de réduction
# --- Don't modify anything beyond this point ---

logging.getLogger().setLevel(logging.INFO)
log_format = "(%(asctime)s)[%(levelname)s] %(message)s"
logging.basicConfig(format=log_format)
logging.captureWarnings(True)

while True:
    file_names = os.listdir(source_dir)
    if(file_names):
        print("Fichier trouvé, déplacement..")
        for file_name in file_names:
            old_path = os.path.join(source_dir, file_name)
            new_path = os.path.join(target_dir, file_name)
            shutil.move(old_path, new_path)
            print("Fichier {0} déplacé vers {1}".format(old_path, new_path))
    time.sleep(2)

def compress_images(pics_to_compress):
    for f in pics_to_compress:
        cmd_line = '{} -q {} -e -o "{}" "{}"'.format(path_to_caesiumclt_exe, compression_factor, folder_to_watch, f)
		# pour ajouter une réduction de résolution, supprimer la ligne cmd au dessus et ajouter celle en dessous :
		# cmd_line = '{} -q {} -e -s {} -o "{}" "{}"'.format(path_to_caesiumclt_exe, compression_factor, scale_factor, folder_to_watch, f)
        logging.info("Compressing {}...".format(f))
        res = subprocess.run(cmd_line, capture_output=True)
        logging.info(res.stdout.decode())
        if res.returncode != 0:
            logging.error("Compression of {} failed with code {}".format(f, res.returncode))
        else:
            logging.info("Compression successful!")


def get_images_since(last_mod_time):
    imgs = []
    for f in os.listdir(folder_to_watch):
        full_path = os.path.join(folder_to_watch, f)
        if full_path.lower().endswith('jpg')\
                and full_path not in last_compressed_pics \
                and datetime.datetime.fromtimestamp(os.stat(full_path).st_ctime) > last_mod_time:
            imgs.append(full_path)
    return imgs


def compress_all_images_in_folder():
    logging.info("Compressing all images in {}".format(folder_to_watch))
    images = []
    for f in os.listdir(folder_to_watch):
        if f.lower().endswith('jpg'):
            full_path = os.path.join(folder_to_watch, f)
            images.append(full_path)
    compress_images(images)
    return images

first_pass = True
last_update = datetime.datetime.now()
last_compressed_pics = []
while True:
    if first_pass and compress_existing_images:
        now = datetime.datetime.now()
        last_compressed_pics = compress_all_images_in_folder()
        first_pass = False
        continue
    now = datetime.datetime.now()
    files = get_images_since(last_update)
    logging.info("{} images to compress".format(len(files)))
    compress_images(files)
    last_compressed_pics = files
    last_update = now
    time.sleep(wait_time_between_checks)
