"""Tesseract OCR wrapper for poker table text recognition."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pytesseract
from PIL import Image

import config
from pokerlens.utils.image_utils import (
    apply_adaptive_threshold,
    apply_threshold,
    preprocess_for_ocr,
    resize_image,
)


@dataclass
class OCRResult:
    """Result from OCR operation."""

    text: str
    confidence: float


class OCREngine:
    """Tesseract OCR wrapper optimized for poker tables."""

    POKER_CHARS_WHITELIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789$.,€£ "

    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize OCR engine.

        Args:
            tesseract_cmd: Path to tesseract executable. If None, uses system default.
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        elif config.DEFAULT_TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = config.DEFAULT_TESSERACT_PATH

    def read_text(
        self,
        image: Image.Image,
        region: Optional[tuple[int, int, int, int]] = None,
        preprocess: bool = True,
        psm: int = config.OCR_PSM_SINGLE_LINE,
    ) -> OCRResult:
        """
        Read text from image.

        Args:
            image: PIL Image to read.
            region: Optional region (x, y, width, height) to crop.
            preprocess: Whether to apply preprocessing.
            psm: Page segmentation mode (7=single line, 8=single word).

        Returns:
            OCRResult with text and confidence.
        """
        if region:
            x, y, w, h = region
            image = image.crop((x, y, x + w, y + h))

        if preprocess:
            image = preprocess_for_ocr(image)

        custom_config = f"--psm {psm} -c tessedit_char_whitelist={self.POKER_CHARS_WHITELIST}"

        try:
            text = pytesseract.image_to_string(
                image, lang=config.OCR_LANG, config=custom_config
            ).strip()

            data = pytesseract.image_to_data(
                image, lang=config.OCR_LANG, config=custom_config, output_type=pytesseract.Output.DICT
            )

            confidences = [
                float(conf) for conf in data.get("conf", []) if conf != "-1"
            ]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return OCRResult(text=text, confidence=avg_confidence)

        except Exception as e:
            return OCRResult(text="", confidence=0.0)

    def read_number(
        self,
        image: Image.Image,
        region: Optional[tuple[int, int, int, int]] = None,
        preprocess: bool = True,
    ) -> OCRResult:
        """
        Read numeric value from image.

        Args:
            image: PIL Image to read.
            region: Optional region to crop.
            preprocess: Whether to apply preprocessing.

        Returns:
            OCRResult with numeric text and confidence.
        """
        if region:
            x, y, w, h = region
            image = image.crop((x, y, x + w, y + h))

        if preprocess:
            image = preprocess_for_ocr(image)

        custom_config = f"--psm {config.OCR_PSM_SINGLE_WORD} -c tessedit_char_whitelist=0123456789$.,€£"

        try:
            text = pytesseract.image_to_string(
                image, lang=config.OCR_LANG, config=custom_config
            ).strip()

            data = pytesseract.image_to_data(
                image, lang=config.OCR_LANG, config=custom_config, output_type=pytesseract.Output.DICT
            )

            confidences = [
                float(conf) for conf in data.get("conf", []) if conf != "-1"
            ]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return OCRResult(text=text, confidence=avg_confidence)

        except Exception as e:
            return OCRResult(text="", confidence=0.0)

    def read_with_fallback(
        self,
        image: Image.Image,
        region: Optional[tuple[int, int, int, int]] = None,
        min_confidence: float = 60.0,
    ) -> OCRResult:
        """
        Read text with fallback preprocessing strategies.

        Args:
            image: PIL Image to read.
            region: Optional region to crop.
            min_confidence: Minimum confidence threshold.

        Returns:
            Best OCRResult from all strategies.
        """
        if region:
            x, y, w, h = region
            image = image.crop((x, y, x + w, y + h))

        strategies = [
            lambda img: preprocess_for_ocr(img, threshold=True),
            lambda img: preprocess_for_ocr(img, threshold=False),
            lambda img: apply_adaptive_threshold(resize_image(img, 2.5), invert=True),
            lambda img: apply_threshold(resize_image(img, 3.0), 150, invert=False),
        ]

        best_result = OCRResult(text="", confidence=0.0)

        for strategy in strategies:
            try:
                processed = strategy(image)
                result = self.read_text(processed, preprocess=False)

                if result.confidence > best_result.confidence:
                    best_result = result

                if result.confidence >= min_confidence:
                    break

            except Exception:
                continue

        return best_result
