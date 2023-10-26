from PIL import Image
import io
import pybase64

def binary_2_image(str_data):
    """
    Принимает на вход строковое представление изображения (type: str), 
    преобразует строку в бинарную строку, после чего восстанавливает изображение

    возвращает изображение (PIL.[Png/Jpeg]ImagePlugin.[Png/Jpeg]ImageFile )
    """
    # преобразуем строку в бинарную строку 
    comma_idx = str_data.rfind(',')
    str_data = str_data[comma_idx + 1:]

    binary_data = str_data.encode('raw_unicode_escape')
    binary_data = pybase64.b64decode((binary_data))

    # Преобразование бинарных данных в объект BytesIO
    image_bytes = io.BytesIO(binary_data)

    # Открываем изображение с помощью Pillow
    image = Image.open(image_bytes)

    return image

def get_image_params(image):
    """
    Получает изображение (PIL.[Png/Jpeg]ImagePlugin.[Png/Jpeg]ImageFile)

    Возвращает его ширину, высоту 
    """

    return image.width, image.height

def save_image(image, path_to_save):
    """
    Сохраняет изображение в указанный файл
    """
    image.save(path_to_save)





