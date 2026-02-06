"""Image preprocessing utilities for OCR optimization."""
from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


def to_grayscale(image: Image.Image) -> Image.Image:
    """
    Convert image to grayscale.

    Args:
        image: Input PIL Image.

    Returns:
        Grayscale PIL Image.
    """
    return image.convert("L")


def to_opencv(image: Image.Image) -> np.ndarray:
    """
    Convert PIL Image to OpenCV format.

    Args:
        image: Input PIL Image.

    Returns:
        OpenCV numpy array (BGR or grayscale).
    """
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def to_pil(cv_image: np.ndarray) -> Image.Image:
    """
    Convert OpenCV image to PIL format.

    Args:
        cv_image: OpenCV numpy array.

    Returns:
        PIL Image.
    """
    if len(cv_image.shape) == 2:
        return Image.fromarray(cv_image, mode="L")
    else:
        return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))


def apply_threshold(
    image: Image.Image, threshold_value: int = 127, invert: bool = False
) -> Image.Image:
    """
    Apply binary threshold to image.

    Args:
        image: Input PIL Image (will be converted to grayscale).
        threshold_value: Threshold value (0-255).
        invert: If True, invert the threshold.

    Returns:
        Thresholded PIL Image.
    """
    gray = to_grayscale(image)
    cv_img = np.array(gray)

    thresh_type = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
    _, thresh = cv2.threshold(cv_img, threshold_value, 255, thresh_type)

    return Image.fromarray(thresh)


def apply_adaptive_threshold(
    image: Image.Image, block_size: int = 11, c: int = 2, invert: bool = False
) -> Image.Image:
    """
    Apply adaptive threshold for varying lighting conditions.

    Args:
        image: Input PIL Image.
        block_size: Size of pixel neighborhood (must be odd).
        c: Constant subtracted from mean.
        invert: If True, invert the threshold.

    Returns:
        Adaptively thresholded PIL Image.
    """
    gray = to_grayscale(image)
    cv_img = np.array(gray)

    thresh_type = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
    output_type = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY

    thresh = cv2.adaptiveThreshold(
        cv_img, 255, thresh_type, output_type, block_size, c
    )

    return Image.fromarray(thresh)


def enhance_contrast(image: Image.Image, clip_limit: float = 2.0) -> Image.Image:
    """
    Enhance image contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization).

    Args:
        image: Input PIL Image.
        clip_limit: Contrast limit for CLAHE.

    Returns:
        Contrast-enhanced PIL Image.
    """
    gray = to_grayscale(image)
    cv_img = np.array(gray)

    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
    enhanced = clahe.apply(cv_img)

    return Image.fromarray(enhanced)


def reduce_noise(image: Image.Image, kernel_size: int = 3) -> Image.Image:
    """
    Reduce noise using median blur.

    Args:
        image: Input PIL Image.
        kernel_size: Median filter kernel size (must be odd).

    Returns:
        Denoised PIL Image.
    """
    cv_img = to_opencv(image)
    denoised = cv2.medianBlur(cv_img, kernel_size)
    return to_pil(denoised)


def resize_image(image: Image.Image, scale: float = 2.0) -> Image.Image:
    """
    Resize image for better OCR accuracy.

    Args:
        image: Input PIL Image.
        scale: Scaling factor.

    Returns:
        Resized PIL Image.
    """
    new_width = int(image.width * scale)
    new_height = int(image.height * scale)
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def preprocess_for_ocr(
    image: Image.Image,
    grayscale: bool = True,
    denoise: bool = True,
    enhance: bool = True,
    threshold: bool = True,
    scale: float = 2.0,
) -> Image.Image:
    """
    Full preprocessing pipeline for OCR optimization.

    Args:
        image: Input PIL Image.
        grayscale: Convert to grayscale.
        denoise: Apply noise reduction.
        enhance: Enhance contrast.
        threshold: Apply adaptive thresholding.
        scale: Upscaling factor.

    Returns:
        Preprocessed PIL Image.
    """
    processed = image

    if scale != 1.0:
        processed = resize_image(processed, scale)

    if grayscale:
        processed = to_grayscale(processed)

    if denoise:
        processed = reduce_noise(processed)

    if enhance:
        processed = enhance_contrast(processed)

    if threshold:
        processed = apply_adaptive_threshold(processed)

    return processed
