import fitz  # PyMuPDF
import os

def optimize_pdf(input_path: str, output_path: str, level: str = "medium") -> bool:
    """
    Optimize PDF to reduce file size.
    level: "light", "medium", "strong"
    Uses PyMuPDF's save with garbage collection, deflate, and image recompression.
    Returns True on success.
    """
    try:
        doc = fitz.open(input_path)
        # Determine parameters based on level
        if level == "light":
            garbage = 1
            deflate = True
            # No image recompression
        elif level == "strong":
            garbage = 2
            deflate = True
            # Use image recompression with quality 80
        else:  # medium
            garbage = 2
            deflate = True
        # Save options
        # For image recompression we can use `deflate_images=True` and `image_quality`
        # PyMuPDF's save: garbage, deflate, deflate_images, image_quality
        # We'll apply image recompression only for medium and strong
        if level == "light":
            doc.save(output_path, garbage=garbage, deflate=deflate)
        else:
            # For medium and strong, also compress images
            # image_quality: 0-100, lower means more compression
            quality = 80 if level == "medium" else 60
            doc.save(output_path, garbage=garbage, deflate=deflate, deflate_images=True, image_quality=quality)
        doc.close()
        return True
    except Exception as e:
        print(f"Error optimizing PDF: {e}")
        return False