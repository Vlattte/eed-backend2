from PIL import Image
import io

def binary_2_image(str_data):
    """
    Принимает на вход строковое представление изображения (type: str), 
    преобразует строку в бинарную строку, после чего восстанавливает изображение

    возвращает изображение (PIL.[Png/Jpeg]ImagePlugin.[Png/Jpeg]ImageFile )
    """
    # преобразуем строку в бинарную строку 
    binary_data = str_data.encode('raw_unicode_escape')

    # Преобразование бинарных данных в объект BytesIO
    image_bytes = io.BytesIO(binary_data)

    # Открываем изображение с помощью Pillow
    image = Image.open(image_bytes)

    # Закрываем объект BytesIO
    image_bytes.close()

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





