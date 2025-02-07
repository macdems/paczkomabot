from io import BytesIO

import qrcode
from qrcode.constants import ERROR_CORRECT_H as QH
from qrcode.constants import ERROR_CORRECT_M as QM


def make_qrcode(data, name, ec, bs, b):
    qr = qrcode.QRCode(version=3, error_correction=ec, box_size=bs, border=b)
    qr.add_data(data)
    img = BytesIO()
    qr.make_image().save(img, 'JPEG')
    img.name = name
    img.seek(0)
    return img


def qrcode_inpost(phone, code, thumb=False):
    return make_qrcode(f'P|{phone}|{code}', f'paczkomat-qr-{phone}-{code}.jpg', QH, 10, 1)


def qrcode_dhl(parcel, pin, thumb=False):
    return make_qrcode(f'{pin}|{parcel}', f'dhl-qr-{parcel}-{pin}.jpg', QM, 12, 6)
