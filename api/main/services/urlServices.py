import qrcode, uuid, os
from flask import current_app


def generateQrCode(url):
    # Create a QR code instance
    qr = qrcode.QRCode(
        version=2,  # The version parameter controls the size of the QR code. Higher value generates a larger QR code.
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # Specify the error correction level. 'M' provides good reliability.
        box_size=10,  # The box_size parameter controls how many pixels each "box" of the QR code is.
        border=4,  # The border parameter controls the size of the white border around the QR code.
    )

    # Add data to the QR code
    # data = "Hello, World!"  # The data you want to encode in the QR code
    data = url
    qr.add_data(data)

    # Generate the QR code
    qr.make(fit=True)

    # Create an image from the QR code
    image = qr.make_image(fill_color="black", back_color="white")

    # file_name = 'qr' + str(uuid.uuid4().time_low)

    # # Save the image
    # image.save(os.path.join(current_app.config["UPLOAD_FOLDER"], file_name))

    return image
