import customtkinter as ctk
from nyquist import NyquistAnnotationApp
from bode import BodeAnnotationApp


class NyquistBodeAnnotationApp:
    def __init__(self):
        self.graph_type = None
        self.mode_type = None
        self.root = None
        self.launch_initial_screen()

    def launch_initial_screen(self):
        # Configurar janela inicial usando CustomTkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Extrator de Dados - Nyquist/Bode Annotation Tool")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        # Título
        title_label = ctk.CTkLabel(self.root, text="Ferramenta de Extração de Dados", font=("Manrope", 22, "bold"))
        title_label.pack(pady=20)

        # Seletor de tipo de gráfico
        self.graph_type = ctk.StringVar(value="nyquist")
        nyquist_button = ctk.CTkRadioButton(self.root, text="Nyquist", variable=self.graph_type, value="nyquist")
        bode_button = ctk.CTkRadioButton(self.root, text="Bode", variable=self.graph_type, value="bode")
        nyquist_button.pack(pady=5)
        bode_button.pack(pady=5)

        # Seletor de modo
        self.mode_type = ctk.StringVar(value="manual")
        manual_button = ctk.CTkRadioButton(self.root, text="Manual", variable=self.mode_type, value="manual")
        automatic_button = ctk.CTkRadioButton(self.root, text="Automático", variable=self.mode_type, value="automatic")
        manual_button.pack(pady=5)
        automatic_button.pack(pady=5)

        # Botão para confirmar a seleção e prosseguir
        confirm_button = ctk.CTkButton(self.root, text="Confirmar Tipo de Gráfico", font=("Manrope", 16),
                                       command=self.confirm_graph_type)
        confirm_button.pack(pady=15)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def confirm_graph_type(self):
        graph_type = self.graph_type.get()
        mode_type = self.mode_type.get()
        print(f"Modo selecionado: {mode_type}, Tipo de gráfico: {graph_type}")
        self.root.destroy()

        # Direciona para o tipo de gráfico e modo apropriados
        if graph_type == "nyquist":
            NyquistAnnotationApp(mode_type)  # Passa o modo selecionado ("manual" ou "automatic")
        elif graph_type == "bode":
            BodeAnnotationApp(mode_type)  # Passa o modo selecionado ("manual" ou "automatic")

    def on_closing(self):
        if self.root is not None:
            self.root.destroy()
            self.root = None


if __name__ == "__main__":
    NyquistBodeAnnotationApp()
