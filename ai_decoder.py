def decode_ai(image_path, threshold=100):
    """
    Decode a message encoded using AI-powered steganography.
    
    Args:
        image_path (str): Path to the encoded image
        threshold (int): Importance threshold used during encoding
        
    Returns:
        str: Decoded message
    """
    try:
        from PIL import Image
        import numpy as np
        from skimage.filters import sobel
        import cv2
        import logging

        # Validate and load image
        validate_image_path(image_path)
        logger = logging.getLogger(__name__)
        
        # Generate importance map using original R values (LSB cleared)
        def generate_importance_map(image_path):
            img_bgr = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if img_bgr is None:
                raise IOError(f"Failed to load image: {image_path}")
            img_bgr[:, :, 2] = img_bgr[:, :, 2] & 0xFE  # Clear LSB of red channel
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            edges = sobel(gray)
            norm = cv2.normalize(edges, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            return norm
        
        importance_map = generate_importance_map(image_path)
        img = Image.open(image_path).convert('RGB')
        pixels = img.load()
        width, height = img.size
        
        # Generate and sort pixels identically to encoder
        pixel_importance = [
            (x, y, imp)
            for y in range(height)
            for x in range(width)
            if (imp := importance_map[y, x]) >= threshold
        ]
        pixel_importance.sort(key=lambda p: (-p[2], p[0], p[1]))  # Stable sort
        
        # Extract bits
        binary = []
        terminator = '1' * 64 + '11111110'  # 8*FF + FE (72 bits)
        terminator = terminator[:64]  # Correct to 64-bit terminator
        
        for x, y, _ in pixel_importance:
            r, _, _ = pixels[x, y]
            binary.append(str(r & 1))
            if len(binary) >= 64 and ''.join(binary[-64:]) == terminator:
                del binary[-64:]
                break
        
        # Convert to bytes
        byte_array = bytearray()
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                byte_array.append(int(''.join(byte), 2))
        
        # Decode with fallbacks
        try:
            return byte_array.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return byte_array.decode('latin-1')
            except Exception:
                from .lsb_decoder import decode_lsb
                return decode_lsb(image_path)
                
    except Exception as e:
        logger.error(f"Decoding failed: {e}")
        from .lsb_decoder import decode_lsb
        return decode_lsb(image_path)