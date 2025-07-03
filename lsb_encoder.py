"""
LSB (Least Significant Bit) encoder module for steganography.

This module provides functionality to hide messages within images
using the LSB steganography technique.
"""
from PIL import Image
import logging
from .utils import validate_image_path, calculate_max_message_size, create_backup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def encode_lsb(image_path, message, output_path):
    """
    Encode a secret message into an image using LSB steganography.
    
    Args:
        image_path (str): Path to the input image
        message (str): Secret message to encode
        output_path (str): Path to save the encoded image
        
    Returns:
        bool: True if encoding was successful
        
    Raises:
        ValueError: If the message is too large for the image
        IOError: If there's an error processing the image
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
        
        # Open the image
        img = Image.open(image_path)
        pixels = img.load()
        width, height = img.size
        
        # Convert message to binary with terminator
        binary_message = ''.join(format(ord(char), '08b') for char in message) + '11111110'
        
        # Encode the message
        idx = 0
        for y in range(height):
            for x in range(width):
                if idx < len(binary_message):
                    r, g, b = pixels[x, y]
                    # Modify only the least significant bit of the red channel
                    r = (r & ~1) | int(binary_message[idx])
                    idx += 1
                    pixels[x, y] = (r, g, b)
                else:
                    break
        
        # Save the encoded image
        img.save(output_path)
        logger.info(f"Message successfully encoded and saved to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error encoding message: {str(e)}")
        raise

# Modify your encode_lsb function to use all channels

def encode_lsb_multi_channel(image_path, message, output_path, channels=['r', 'g', 'b']):
    """
    Encode a secret message into an image using multi-channel LSB steganography.
    
    Args:
        image_path (str): Path to the input image
        message (str): Secret message to encode
        output_path (str): Path to save the encoded image
        channels (list): List of channels to use ('r', 'g', 'b')
        
    Returns:
        bool: True if encoding was successful
    """
    try:
        # Validate the image path
        validate_image_path(image_path)
        
        # Calculate maximum message size (3x if using all channels)
        channel_count = len(channels)
        max_chars = calculate_max_message_size(image_path) * channel_count
        if len(message) > max_chars:
            raise ValueError(f"Message too large for image. Maximum size: {max_chars} characters")
        
        # Create backup of original image
        create_backup(image_path)
        
        # Open the image
        img = Image.open(image_path)
        pixels = img.load()
        width, height = img.size
        
        # Convert message to binary with terminator
        binary_message = ''.join(format(ord(char), '08b') for char in message) + '11111110'
        
        # Encode the message across multiple channels
        idx = 0
        for y in range(height):
            for x in range(width):
                if idx < len(binary_message):
                    r, g, b = pixels[x, y]
                    
                    # Modify channels based on configuration
                    if 'r' in channels and idx < len(binary_message):
                        r = (r & ~1) | int(binary_message[idx])
                        idx += 1
                    
                    if 'g' in channels and idx < len(binary_message):
                        g = (g & ~1) | int(binary_message[idx])
                        idx += 1
                    
                    if 'b' in channels and idx < len(binary_message):
                        b = (b & ~1) | int(binary_message[idx])
                        idx += 1
                    
                    pixels[x, y] = (r, g, b)
                else:
                    break
        
        # Save the encoded image
        img.save(output_path)
        logger.info(f"Message successfully encoded using multiple channels and saved to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error encoding message: {str(e)}")
        raise