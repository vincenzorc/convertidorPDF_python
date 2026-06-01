from views.main_window import MainWindow
from views.image_tab import ImageTab
from views.pdf_tools_tab import PdfToolsTab
from controllers.image_controller import ImageController
from controllers.pdf_controller import PdfController


def main():
    app = MainWindow()

    image_frame = app.add_tab("Imagen a PDF")
    image_view = ImageTab(image_frame)
    ImageController(image_view, app)

    pdf_frame = app.add_tab("Herramientas PDF")
    pdf_view = PdfToolsTab(pdf_frame)
    PdfController(pdf_view, app)

    app.mainloop()


if __name__ == "__main__":
    main()
