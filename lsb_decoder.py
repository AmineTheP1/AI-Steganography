"""
LSB (Least Significant Bit) decoder module for steganography.

This module provides functionality to extract hidden messages from images
that were encoded using the LSB steganography technique.
"""
from PIL import Image
import logging
from .utils import validate_image_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def decode_lsb(image_path):
    """
    Decode a secret message from an image using LSB steganography.
    
    Args:
        image_path (str): Path to the encoded image
        
    Returns:
        str: Decoded secret message
        
    Raises:
        ValueError: If no valid message is found
        IOError: If there's an error processing the image
    """
    try:
        # Validate the image path
        validate_image_path(image_path)
        
        # Open the image
        img = Image.open(image_path)
        pixels = img.load()
        width, height = img.size
        
        # Extract binary message
        binary = ''
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                binary += str(r & 1)  # Extract LSB from red channel
                
                # Check for terminator every 8 bits
                if len(binary) % 8 == 0 and len(binary) >= 8:
                    if binary[-8:] == '11111110':
                        # Found terminator, stop extraction
                        binary = binary[:-8]  # Remove terminator
                        break
            else:
                continue
            break
        
        # Convert binary to characters
        chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
        message = ''
        for char in chars:
            if len(char) == 8:  # Ensure we have a full byte
                message += chr(int(char, 2))
        
        if not message:
            logger.warning("No message found in the image")
            return ""
            
        logger.info(f"Successfully decoded message of length {len(message)}")
        return message
        
    except Exception as e:
        logger.error(f"Error decoding message: {str(e)}")
        raise


def detect_encoding_format(image_path):
    """
    Attempt to detect the encoding format used in an image.
    
    Args:
        image_path (str): Path to the encoded image
        
    Returns:
        str: Detected format ('stegai', 'standard', 'unknown')
    """
    try:
        # Try different decoding methods and see which one produces valid results
        # This is a simplified example - you would need more sophisticated detection
        
        # Try StegAI format first
        try:
            message = decode_lsb(image_path)
            if message:
                return 'stegai'
        except Exception:
            pass
        
        # Try standard format (all channels, no terminator)
        try:
            message = decode_standard_lsb(image_path)
            if message:
                return 'standard'
        except Exception:
            pass
        
        return 'unknown'
        
    except Exception as e:
        logger.error(f"Error detecting encoding format: {str(e)}")
        return 'unknown'

def decode_standard_lsb(image_path):
    """
    Decode a message using standard LSB steganography format.
    This attempts to be compatible with common online tools.
    
    Args:
        image_path (str): Path to the encoded image
        
    Returns:
        str: Decoded message
    """
    try:
        # Validate the image path
        validate_image_path(image_path)
        
        # Open the image
        img = Image.open(image_path)
        pixels = img.load()
        width, height = img.size
        
        # Extract binary message from all channels
        binary = ''
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                binary += str(r & 1)  # Red channel
                binary += str(g & 1)  # Green channel
                binary += str(b & 1)  # Blue channel
                
                # Check for null terminator
                if len(binary) % 8 == 0 and len(binary) >= 8:
                    last_byte = binary[-8:]
                    if last_byte == '00000000':
                        binary = binary[:-8]
                        break
            else:
                continue
            break
        
        # Convert binary to characters
        chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
        message = ''
        for char in chars:
            if len(char) == 8:  # Ensure we have a full byte
                message += chr(int(char, 2))
        
        return message
        
    except Exception as e:
        logger.error(f"Error decoding standard format: {str(e)}")
        raise