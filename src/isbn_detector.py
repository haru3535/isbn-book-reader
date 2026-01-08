from typing import List, Union
from PIL import Image
import numpy as np
from pyzbar import pyzbar
import cv2


class ISBNDetector:
    def detect_isbn(self, image: Union[Image.Image, np.ndarray]) -> List[str]:
        if isinstance(image, Image.Image):
            image = np.array(image)

        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        isbns = []

        images_to_try = [
            image,
            self.preprocess_image(image),
            self._preprocess_simple(image),
            self._preprocess_enhanced(image)
        ]

        for img in images_to_try:
            barcodes = pyzbar.decode(img)
            for barcode in barcodes:
                if barcode.type in ['EAN13', 'EAN-13']:
                    code = barcode.data.decode('utf-8')
                    if (code.startswith('978') or code.startswith('979')) and self.validate_isbn(code):
                        isbns.append(code)

        return list(set(isbns))

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(blurred)

        binary = cv2.adaptiveThreshold(
            contrast, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            35, 15
        )

        return binary

    def _preprocess_simple(self, image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary

    def _preprocess_enhanced(self, image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        sharpening_kernel = np.array([[-1, -1, -1],
                                       [-1,  9, -1],
                                       [-1, -1, -1]])
        sharpened = cv2.filter2D(denoised, -1, sharpening_kernel)

        binary = cv2.adaptiveThreshold(
            sharpened, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        return binary

    def validate_isbn(self, code: str) -> bool:
        code = code.replace('-', '').replace(' ', '')

        if len(code) == 13:
            return self._validate_isbn13(code)
        elif len(code) == 10:
            return self._validate_isbn10(code)
        else:
            return False

    def _validate_isbn13(self, isbn: str) -> bool:
        if not isbn.isdigit() or len(isbn) != 13:
            return False

        checksum = 0
        for i, digit in enumerate(isbn[:-1]):
            if i % 2 == 0:
                checksum += int(digit)
            else:
                checksum += int(digit) * 3

        check_digit = (10 - (checksum % 10)) % 10
        return check_digit == int(isbn[-1])

    def _validate_isbn10(self, isbn: str) -> bool:
        if len(isbn) != 10:
            return False

        checksum = 0
        for i, char in enumerate(isbn[:-1]):
            if not char.isdigit():
                return False
            checksum += int(char) * (10 - i)

        last_char = isbn[-1]
        if last_char == 'X':
            checksum += 10
        elif last_char.isdigit():
            checksum += int(last_char)
        else:
            return False

        return checksum % 11 == 0
