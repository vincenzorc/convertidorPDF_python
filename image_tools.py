from PIL import Image
from typing import List
import traceback

def images_to_pdf(
    image_paths: List[str],
    output_path: str,
    page_size: str = "Sin formato",
    margins: str = "Sin margenes",
    orientation: str = "Vertical",
) -> bool:
    """
    Convert a list of image paths to a single PDF file with optional page sizing, margins and orientation.
    
    Args:
        image_paths: List of paths to image files
        output_path: Path for output PDF
        page_size: Page size format ("Sin formato", "A4", "Carta", "Legal")
        margins: Margin setting ("Sin margenes", "Poco", "Medio", "Mucho")
        orientation: Page orientation ("Vertical" or "Horizontal")
        
    Returns:
        True on success, False on failure
    """
    if not image_paths:
        return False
    
    try:
        # Define page sizes in points (1 point = 1/72 inch)
        PAGE_SIZES = {
            "Sin formato": None,       # Use original image size
            "A4": (595.0, 842.0),      # A4: 210mm x 297mm
            "Carta": (612.0, 792.0),   # Letter: 8.5in x 11in
            "Legal": (612.0, 1008.0),  # Legal: 8.5in x 14in
        }

        # Define margins in points
        MARGIN_POINTS = {
            "Sin margenes": 0.0,
            "Poco": 18.0,
            "Medio": 36.0,
            "Mucho": 54.0,
        }
        
        if page_size not in PAGE_SIZES:
            page_size = "Sin formato"

        if margins not in MARGIN_POINTS:
            margins = "Sin margenes"

        target_size = PAGE_SIZES[page_size]

        if target_size is not None and orientation == "Horizontal":
            page_width, page_height = target_size
            target_size = (page_height, page_width)

        margin_points = MARGIN_POINTS[margins]

        if hasattr(Image, "Resampling"):
            resample_filter = Image.Resampling.LANCZOS
        else:
            resample_filter = Image.LANCZOS
        
        images = []
        for img_path in image_paths:
            try:
                with Image.open(img_path) as img:
                    # Force load image data to catch errors early
                    img.load()
                    
                    # Handle transparency and mode conversion
                    if img.mode == "RGBA":
                        # Create white background
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        # Paste using alpha channel as mask
                        background.paste(img, mask=img.split()[3])  # 3 is alpha
                        img = background
                    elif img.mode == "LA":
                        # LA: Luminance + Alpha
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        # Convert LA to RGBA then paste
                        rgba_img = img.convert("RGBA")
                        background.paste(rgba_img, mask=rgba_img.split()[3])  # alpha channel
                        img = background
                    elif img.mode == "P":
                        # Palette mode, may have transparency
                        # Convert to RGBA to handle transparency if present
                        img = img.convert("RGBA")
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3])
                        img = background
                    else:
                        # For RGB, L (grayscale), CMYK, etc., convert to RGB
                        img = img.convert("RGB")
                    
                    # If we have a target page size, resize and position the image
                    if target_size is not None:
                        img_width, img_height = img.size
                        page_width, page_height = target_size

                        # Calculate margins
                        margin_x = margin_points
                        margin_y = margin_points

                        # Calculate available space for image
                        available_width = page_width - 2 * margin_x
                        available_height = page_height - 2 * margin_y

                        if available_width <= 0 or available_height <= 0:
                            return False
                        
                        # Calculate scaling factor to fit image within available space
                        scale_w = available_width / img_width
                        scale_h = available_height / img_height
                        scale = min(scale_w, scale_h)  # Maintain aspect ratio
                        
                        # Calculate new image dimensions
                        new_width = max(1, int(img_width * scale))
                        new_height = max(1, int(img_height * scale))

                        # Resize image
                        img = img.resize((new_width, new_height), resample_filter)
                        
                        # Create new image with page size and white background
                        page_img = Image.new("RGB", (int(page_width), int(page_height)), (255, 255, 255))
                        
                        # Calculate position to center the image
                        x_offset = int((page_width - new_width) / 2)
                        y_offset = int((page_height - new_height) / 2)
                        
                        # Paste resized image onto page
                        page_img.paste(img, (x_offset, y_offset))
                        img = page_img
                    else:
                        # No page size specified, use image as-is (but ensure it's RGB)
                        if img.mode != "RGB":
                            img = img.convert("RGB")
                    
                    images.append(img.copy())
            except Exception as inner_e:
                print(f"Failed to process image {img_path}: {inner_e}")
                traceback.print_exc()
                return False
        
        # Save all images as PDF
        images[0].save(output_path, "PDF", save_all=True, append_images=images[1:])
        return True
    except Exception as e:
        traceback.print_exc()
        print(f"Error converting images to PDF: {e}")
        return False
