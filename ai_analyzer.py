"""
AI-based image analysis module for steganography.

This module provides functionality to analyze images and generate
importance maps that can be used to improve steganography techniques.
"""
import cv2
import numpy as np
from skimage.filters import sobel
import logging
from PIL import Image
import os
from .utils import validate_image_path, calculate_max_message_size
from .ai_encoder import encode_ai
from .ai_decoder import decode_ai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_backup(image_path):
    """
    Create a backup of the original image before encoding.
    
    Args:
        image_path (str): Path to the original image
    """
    backup_path = f"{os.path.splitext(image_path)[0]}_backup{os.path.splitext(image_path)[1]}"
    try:
        img = Image.open(image_path)
        img.save(backup_path)
        logger.info(f"Created backup at {backup_path}")
    except Exception as e:
        logger.warning(f"Failed to create backup: {str(e)}")

def generate_importance_map(image_path):
    """
    Generate an importance map for an image based on edge detection.
    
    The importance map highlights areas of the image with high texture/detail,
    which are better suited for hiding information with minimal visual impact.
    
    Args:
        image_path (str): Path to the input image
        
    Returns:
        numpy.ndarray: Importance map (0-255 values)
        
    Raises:
        IOError: If there's an error processing the image
    """
    try:
        # Validate the image path
        validate_image_path(image_path)
        
        # Load the image in grayscale
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise IOError(f"Failed to load image: {image_path}")
        
        # Apply Sobel edge detection
        edges = sobel(img)
        
        # Normalize to 0-255 range
        norm = cv2.normalize(edges, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        logger.info(f"Generated importance map for {image_path}")
        return norm
        
    except Exception as e:
        logger.error(f"Error generating importance map: {str(e)}")
        raise

# Wrapper functions to maintain backward compatibility
def smart_encode(image_path, message, output_path, threshold=100):
    """
    Wrapper for encode_ai function.
    
    Args:
        image_path (str): Path to the input image
        message (str): Secret message to encode
        output_path (str): Path to save the encoded image
        threshold (int): Importance threshold (0-255)
        
    Returns:
        bool: True if encoding was successful
    """
    return encode_ai(image_path, message, output_path, threshold)

def smart_decode(image_path, threshold=100):
    """
    Wrapper for decode_ai function.
    
    Args:
        image_path (str): Path to the encoded image
        threshold (int): Importance threshold (0-255)
        
    Returns:
        str: Decoded secret message
    """
    return decode_ai(image_path, threshold)