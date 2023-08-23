from io import BytesIO

import qrcode


def make_qr_code_image(phone, code, thumb=False):
    qr = qrcode.QRCode(version=3, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=1)
    qr.add_data(f'P|{phone}|{code}')
    img = BytesIO()
    img.name = f'paczkomat-qr-{phone}-{code}.jpg'
    qr.make_image().save(img, 'JPEG')
    img.seek(0)
    return img
