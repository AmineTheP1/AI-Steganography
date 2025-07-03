"""
AI-based encoding module for steganography.

This module provides functionality to encode messages into images
using AI-powered importance maps for optimal pixel selection.
"""
import cv2
import numpy as np
from skimage.filters import sobel
import logging
from PIL import Image
import os
from .utils import validate_image_path, calculate_max_message_size

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

def encode_ai(image_path, message, output_path, threshold=100):
    """
    Encode a message using importance map to select optimal pixels.
    
    This function uses the importance map to prioritize encoding in
    high-texture areas where changes are less noticeable.
    
    Args:
        image_path (str): Path to the input image
        message (str): Secret message to encode
        output_path (str): Path to save the encoded image
        threshold (int): Importance threshold (0-255)
        
    Returns:
        bool: True if encoding was successful
    """
    try:
        # Validate the image path
        validate_image_path(image_path)
        
        # Calculate maximum message size
        max_chars = calculate_max_message_size(image_path)
        if len(message) > max_chars:
            raise ValueError(f"Message too large for image. Maximum size: {max_chars} characters")
        
        # Create backup of original image
        create_backup(image_path)
        
        # Generate importance map
        print("Generating importance map for intelligent pixel selection...")
        importance_map = generate_importance_map(image_path)
        
        # Open the image and force RGB mode
        img = Image.open(image_path).convert('RGB')
        pixels = img.load()
        width, height = img.size
        
        # Debug info
        print(f"AI-powered encoding activated")
        print(f"Using importance threshold: {threshold}")
        print(f"Message length: {len(message)} characters")
        print(f"Image dimensions: {width}x{height}")
        
        # Create a list of pixel coordinates sorted by importance
        pixel_importance = []
        for y in range(height):
            for x in range(width):
                if importance_map[y, x] >= threshold:
                    pixel_importance.append((x, y, importance_map[y, x]))
        
        # Sort pixels by importance (highest first)
        pixel_importance.sort(key=lambda p: p[2], reverse=True)
        print(f"Found {len(pixel_importance)} pixels above threshold")
        
        # Convert message to UTF-8 bytes, then to binary string
        message_bytes = message.encode('utf-8')
        binary_message = ''
        for byte in message_bytes:
            binary_message += format(byte, '08b')
        
        # Add terminator (8 bytes of 0xFF followed by 0xFE)
        binary_message += '1111111111111111111111111111111111111111111111111111111111111110'
        
        # Check if we have enough pixels
        if len(binary_message) > len(pixel_importance):
            raise ValueError(f"Not enough suitable pixels for encoding. Need {len(binary_message)}, found {len(pixel_importance)}")
        
        # Encode the message in the selected pixels
        for idx, bit in enumerate(binary_message):
            if idx < len(pixel_importance):
                x, y, _ = pixel_importance[idx]
                r, g, b = pixels[x, y]
                # Modify only the least significant bit of the red channel
                r = (r & ~1) | int(bit)
                pixels[x, y] = (r, g, b)
        
        # Save the encoded image as PNG to avoid compression issues
        output_path_png = os.path.splitext(output_path)[0] + '.png'
        img.save(output_path_png, 'PNG')
        print(f"Message successfully encoded and saved to {output_path_png}")
        logger.info(f"Message successfully encoded using AI-powered encoding and saved to {output_path_png}")
        return True
        
    except Exception as e:
        logger.error(f"Error encoding message with AI-powered encoding: {str(e)}")
        raise