import pytest
import numpy as np
from PIL import Image
from src.isbn_detector import ISBNDetector


class TestISBNDetector:
    def setup_method(self):
        self.detector = ISBNDetector()

    def test_validate_isbn13_checksum_valid(self):
        valid_isbn13 = "9784839974206"
        assert self.detector.validate_isbn(valid_isbn13) is True

    def test_validate_isbn13_checksum_invalid(self):
        invalid_isbn13 = "9784839974207"
        assert self.detector.validate_isbn(invalid_isbn13) is False

    def test_validate_isbn10_checksum_valid(self):
        valid_isbn10 = "4839974209"
        assert self.detector.validate_isbn(valid_isbn10) is True

    def test_validate_isbn10_checksum_invalid(self):
        invalid_isbn10 = "4839974208"
        assert self.detector.validate_isbn(invalid_isbn10) is False

    def test_validate_isbn_wrong_length(self):
        invalid_isbn = "123456789"
        assert self.detector.validate_isbn(invalid_isbn) is False

    def test_preprocess_image_returns_grayscale(self):
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[:, :] = [255, 0, 0]

        processed = self.detector.preprocess_image(test_image)

        assert processed is not None
        assert len(processed.shape) == 2

    def test_preprocess_image_returns_uint8(self):
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)

        processed = self.detector.preprocess_image(test_image)

        assert processed.dtype == np.uint8

    def test_detect_isbn_returns_list(self):
        test_image = Image.new('RGB', (100, 100))

        result = self.detector.detect_isbn(test_image)

        assert isinstance(result, list)

    def test_detect_isbn_accepts_numpy_array(self):
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)

        result = self.detector.detect_isbn(test_image)

        assert isinstance(result, list)
