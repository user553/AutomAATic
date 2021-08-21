import base64
import os


class Base64Helper:
    @staticmethod
    def picture_to_base64(image_name):
        try:
            with open('aat_main/resources/images/' + image_name, 'rb') as f:
                base64_code = base64.b64encode(f.read()).decode()
            return 'data:image/jpeg;base64,%s' % base64_code
        except:
            return Exception

    @staticmethod
    def base64_to_picture(base64_data, image_name):
        if base64_data.startswith("data:image/"):
            is_existed = os.path.exists('aat_main/resources/images')
            if not is_existed:
                os.mkdir('aat_main/resources/images')
            img_data = base64.b64decode(base64_data.split(",")[-1].encode("utf-8"))
            with open('aat_main/resources/images/' + image_name, 'wb') as f:
                f.write(img_data)
            return image_name
        else:
            raise Exception
