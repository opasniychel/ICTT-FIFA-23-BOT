import os
import random
import string

# Установка пути к папке, содержащей фотографии
folder_path = "Cards"

# Получение списка имен файлов в папке
file_list = os.listdir(folder_path)

# Цикл переименования файлов
for file_name in file_list:
    # Получение расширения файла
    file_extension = os.path.splitext(file_name)[1]

    # Генерация случайного имени файла
    new_file_name = ''.join(random.choice(string.ascii_letters) for i in range(100))

    # Переименование файла
    os.rename(os.path.join(folder_path, file_name), os.path.join(folder_path, new_file_name + file_extension))


path = "Cards/"
files = os.listdir(path)

i = 1

for file in files:
    if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png") or file.endswith(".gif"):
        os.rename(os.path.join(path, file), os.path.join(path, str(i)+".jpg"))
        i += 1

# Установка пути к папке, содержащей фотографии
folder_path = "Cards"

# Получение списка имен файлов в папке
file_list = os.listdir(folder_path)

# Цикл изменения расширения файлов
for file_name in file_list:
    # Получение расширения файла
    file_extension = os.path.splitext(file_name)[1]

    # Проверка, является ли файл фотографией
    if file_extension.lower() in [".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".png"]:
        # Переименование файла с изменением расширения на .png
        os.rename(os.path.join(folder_path, file_name), os.path.join(folder_path, os.path.splitext(file_name)[0] + ".png"))