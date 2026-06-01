import fitz


class PdfOptimizer:

    def optimize(self, input_path: str, output_path: str, level: str = "medium") -> bool:
        try:
            doc = fitz.open(input_path)
            if level == "light":
                doc.save(output_path, garbage=1, deflate=True)
            elif level == "strong":
                doc.save(output_path, garbage=2, deflate=True, deflate_images=True, image_quality=60)
            else:
                doc.save(output_path, garbage=2, deflate=True, deflate_images=True, image_quality=80)
            doc.close()
            return True
        except Exception as e:
            print(f"Error optimizing PDF: {e}")
            return False
