import customtkinter as ctk
from tkinter import filedialog, messagebox
from image_processing import preprocess_image
from nyquist import NyquistAnnotation
from bode import BodeAnnotation

class NyquistBodeAnnotationApp:
    def __init__(self):
        self.image_path = None
        self.image_path_magnitude = None
        self.image_path_phase = None
        self.x_min = 0
        self.x_max = 1
        self.y_min = 0
        self.y_max = 1
        self.automatic_mode = False

        self.launch_initial_screen()

    def launch_initial_screen(self):
        # Configurar janela inicial
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Extrator de Dados - Nyquist/Bode Annotation Tool")
        self.root.geometry("600x800")
        self.root.resizable(False, False)

        # Título e opções da interface
        title_label = ctk.CTkLabel(self.root, text="Ferramenta de Extração de Dados", font=("Manrope", 22, "bold"))
        title_label.pack(pady=20)

        self.graph_type = ctk.StringVar(value="nyquist")
        nyquist_button = ctk.CTkRadioButton(self.root, text="Nyquist", variable=self.graph_type, value="nyquist")
        bode_button = ctk.CTkRadioButton(self.root, text="Bode", variable=self.graph_type, value="bode")
        nyquist_button.pack(pady=5)
        bode_button.pack(pady=5)

        self.mode_type = ctk.StringVar(value="manual")
        manual_button = ctk.CTkRadioButton(self.root, text="Manual", variable=self.mode_type, value="manual")
        automatic_button = ctk.CTkRadioButton(self.root, text="Automático", variable=self.mode_type, value="automatic")
        manual_button.pack(pady=5)
        automatic_button.pack(pady=5)

        confirm_button = ctk.CTkButton(self.root, text="Confirmar Tipo de Gráfico", font=("Manrope", 16),
                                       command=self.confirm_graph_type)
        confirm_button.pack(pady=15)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def confirm_graph_type(self):
        self.automatic_mode = self.mode_type.get() == "automatic"
        if self.graph_type.get() == "nyquist":
            self.launch_nyquist_screen()
        elif self.graph_type.get() == "bode":
            self.launch_bode_screen()

    def launch_nyquist_screen(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if self.image_path:
            self.image = preprocess_image(self.image_path)
            nyquist_annotation = NyquistAnnotation(self.image, self.x_min, self.x_max, self.y_min, self.y_max)
            nyquist_annotation.start_annotation()

    def launch_bode_screen(self):
        self.image_path_magnitude = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        self.image_path_phase = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if self.image_path_magnitude and self.image_path_phase:
            self.image_magnitude = preprocess_image(self.image_path_magnitude)
            self.image_phase = preprocess_image(self.image_path_phase)
            bode_annotation = BodeAnnotation(self.image_magnitude, self.image_phase, self.x_min, self.x_max)
            bode_annotation.start_annotation()

    def on_closing(self):
        if self.root is not None:
            self.root.destroy()

if __name__ == "__main__":
    NyquistBodeAnnotationApp()
