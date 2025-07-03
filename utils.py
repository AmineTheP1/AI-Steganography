"""
Utility functions for steganography operations.
"""
import os
import logging
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_image_path(image_path):
    """
    Validate that the image path exists and is a supported format.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        bool: True if valid, False otherwise
    
    Raises:
        FileNotFoundError: If the image file doesn't exist
        ValueError: If the image format is not supported
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    supported_formats = ['.png', '.jpg', '.jpeg', '.bmp']
    file_ext = os.path.splitext(image_path)[1].lower()
    
    if file_ext not in supported_formats:
        raise ValueError(f"Unsupported image format: {file_ext}. Supported formats: {supported_formats}")
    
    return True

def calculate_max_message_size(image_path):
    """
    Calculate the maximum message size that can be encoded in an image.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        int: Maximum number of characters that can be encoded
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            # Each pixel can store 1 bit, 8 bits per character
            # Subtract 8 bits for the terminator
            max_bits = width * height - 8
            max_chars = max_bits // 8
            return max_chars
    except Exception as e:
        logger.error(f"Error calculating max message size: {str(e)}")
        raise

def create_backup(image_path):
    """
    Create a backup of the original image.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Path to the backup file
    """
    backup_path = f"{image_path}.backup"
    try:
        with open(image_path, 'rb') as src:
            with open(backup_path, 'wb') as dst:
                dst.write(src.read())
        return backup_path
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        raise

def convert_to_png(image_path, output_path=None):
    """
    Convert an image to PNG format for steganography.
    
    Args:
        image_path (str): Path to the input image
        output_path (str, optional): Path to save the converted image
        
    Returns:
        str: Path to the converted PNG image
    """
    try:
        if output_path is None:
            output_path = os.path.splitext(image_path)[0] + '.png'
        
        img = Image.open(image_path)
        img.save(output_path, 'PNG')
        logger.info(f"Converted image to PNG format: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error converting image to PNG: {str(e)}")
        raise