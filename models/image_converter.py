from PIL import Image
from typing import List
import traceback


class ImageConverter:

    PAGE_SIZES = {
        "Sin formato": None,
        "A4": (595.0, 842.0),
        "Carta": (612.0, 792.0),
        "Legal": (612.0, 1008.0),
    }

    MARGIN_POINTS = {
        "Sin margenes": 0.0,
        "Poco": 18.0,
        "Medio": 36.0,
        "Mucho": 54.0,
    }

    def convert(
        self,
        image_paths: List[str],
        output_path: str,
        page_size: str = "Sin formato",
        margins: str = "Sin margenes",
        orientation: str = "Vertical",
    ) -> bool:
        if not image_paths:
            return False

        if page_size not in self.PAGE_SIZES:
            page_size = "Sin formato"
        if margins not in self.MARGIN_POINTS:
            margins = "Sin margenes"

        target_size = self.PAGE_SIZES[page_size]
        if target_size is not None and orientation == "Horizontal":
            target_size = (target_size[1], target_size[0])

        margin_pts = self.MARGIN_POINTS[margins]

        if hasattr(Image, "Resampling"):
            resample = Image.Resampling.LANCZOS
        else:
            resample = Image.LANCZOS

        try:
            images = []
            for img_path in image_paths:
                try:
                    with Image.open(img_path) as img:
                        img.load()
                        img = self._ensure_rgb(img)

                        if target_size is not None:
                            img = self._fit_to_page(img, target_size, margin_pts, resample)

                        images.append(img.copy())
                except Exception as e:
                    print(f"Failed to process image {img_path}: {e}")
                    traceback.print_exc()
                    return False

            images[0].save(output_path, "PDF", save_all=True, append_images=images[1:])
            return True
        except Exception as e:
            traceback.print_exc()
            print(f"Error converting images to PDF: {e}")
            return False

    def _ensure_rgb(self, img: Image.Image) -> Image.Image:
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            return bg
        elif img.mode == "LA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            rgba = img.convert("RGBA")
            bg.paste(rgba, mask=rgba.split()[3])
            return bg
        elif img.mode == "P":
            img = img.convert("RGBA")
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            return bg
        else:
            return img.convert("RGB")

    def _fit_to_page(self, img, target_size, margin_pts, resample):
        page_w, page_h = target_size
        avail_w = page_w - 2 * margin_pts
        avail_h = page_h - 2 * margin_pts
        if avail_w <= 0 or avail_h <= 0:
            return img

        img_w, img_h = img.size
        scale = min(avail_w / img_w, avail_h / img_h)
        new_w = max(1, int(img_w * scale))
        new_h = max(1, int(img_h * scale))

        img = img.resize((new_w, new_h), resample)
        page_img = Image.new("RGB", (int(page_w), int(page_h)), (255, 255, 255))
        x = int((page_w - new_w) / 2)
        y = int((page_h - new_h) / 2)
        page_img.paste(img, (x, y))
        return page_img
