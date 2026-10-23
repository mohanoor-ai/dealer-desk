"""Decode bounded user images and save only fresh, metadata-free JPEG pixels."""
import base64
import binascii
from io import BytesIO
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_INPUT = 2 * 1024 * 1024
MAX_PIXELS = 20_000_000
MAX_OUTPUT = 200_000
MAX_PHOTOS = 12

def encode_jpeg(image, max_size):
    image = image.copy()
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    for quality in (88, 78, 65, 50):
        output = BytesIO()
        image.save(output, 'JPEG', quality=quality, optimize=True, exif=b'', icc_profile=None)
        content = output.getvalue()
        if len(content) <= MAX_OUTPUT:
            return content, image.width, image.height
    raise ValueError('Image is too complex. Choose a smaller photo.')

def prepare_photo(data_url):
    try:
        header, encoded = data_url.split(',',1)
        if header not in ('data:image/jpeg;base64','data:image/png;base64','data:image/webp;base64'):
            raise ValueError('Choose a JPEG, PNG or WebP image.')
        content = base64.b64decode(encoded, validate=True)
        if len(content) > MAX_INPUT:
            raise ValueError('Each image must be 2 MB or smaller.')
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(BytesIO(content), formats=['JPEG','PNG','WEBP']) as image:
                if image.width * image.height > MAX_PIXELS:
                    raise ValueError('Choose an image below 20 megapixels.')
                if getattr(image,'n_frames',1) != 1:
                    raise ValueError('Choose a still photo, not an animation.')
                image.load()
                oriented = ImageOps.exif_transpose(image).convert('RGBA')
                pixels = Image.new('RGB', oriented.size, 'white')
                pixels.paste(oriented, mask=oriented.getchannel('A'))
                full, width, height = encode_jpeg(pixels, (1600,1200))
                thumbnail, _, _ = encode_jpeg(pixels, (600,450))
        return full, thumbnail, width, height
    except (binascii.Error, UnidentifiedImageError, OSError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as error:
        raise ValueError('This file could not be read as a safe photo. Try another JPEG, PNG or WebP.') from error
