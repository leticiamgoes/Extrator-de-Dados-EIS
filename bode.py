import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import Button, RadioButtons
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.image as mpimg
import image_processing


class BodeAnnotationApp:
    def __init__(self, mode):
        self.image_path_magnitude = None
        self.image_path_phase = None
        self.image_magnitude = None
        self.image_phase = None
        # Para armazenamento de processamento automático
        self.processed_image_magnitude = None
        # Para armazenamento de processamento automático
        self.processed_image_phase = None
        self.refined_curves_magnitude = None
        self.refined_curves_phase = None
        self.x_min = 0
        self.x_max = 1
        self.curves_magnitude = {}
        self.curves_phase = {}
        self.current_curve = []
        self.trace_active = False
        self.current_color = "red"
        self.mode = "points"
        self.annotation_mode = mode
        self.root = None
        self.annotation_root = None
        self.fig = None
        self.ax_magnitude = None
        self.ax_phase = None
        self.canvas = None
        self.toolbar = None

        if self.annotation_mode == "automatic":
            self.launch_bode_automatic_screen()
        else:
            self.launch_bode_screen()

    def launch_bode_automatic_screen(self):
        self.root = ctk.CTk()
        self.root.title(
            "Extrator de Dados - Bode Annotation Tool (Automático)")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        title_label = ctk.CTkLabel(
            self.root, text="Modo Automático: Bode", font=("Manrope", 22, "bold"))
        title_label.pack(pady=20)

        select_image_button_magnitude = ctk.CTkButton(self.root, text="Selecionar Imagem (Magnitude)",
                                                      font=("Manrope", 16), command=self.select_image_magnitude)
        select_image_button_magnitude.pack(pady=10)

        select_image_button_phase = ctk.CTkButton(self.root, text="Selecionar Imagem (Fase)",
                                                  font=("Manrope", 16), command=self.select_image_phase)
        select_image_button_phase.pack(pady=10)

        # Entradas para x_min e x_max
        self.entries = {}
        frame_limits = ctk.CTkFrame(self.root)
        frame_limits.pack(pady=20, padx=40, fill="both", expand=True)
        limits = ["x_min", "x_max"]
        for limit in limits:
            label = ctk.CTkLabel(
                frame_limits, text=f"{limit} (Hz):", font=("Manrope", 14))
            label.grid(row=limits.index(limit), column=0,
                       sticky="e", padx=10, pady=10)
            entry = ctk.CTkEntry(frame_limits, width=150, font=("Manrope", 14))
            entry.grid(row=limits.index(limit), column=1, padx=10, pady=10)
            self.entries[limit] = entry

        # Centralizar os campos de input
        frame_limits.grid_columnconfigure(0, weight=1)
        frame_limits.grid_columnconfigure(1, weight=1)

        start_processing_button = ctk.CTkButton(self.root, text="Processar Imagens", font=("Manrope", 16),
                                                command=self.process_automatic)
        start_processing_button.pack(pady=20)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def select_image_magnitude(self):
        self.image_path_magnitude = filedialog.askopenfilename(
            filetypes=[("Image files", ".png;.jpg;*.jpeg")]
        )
        if self.image_path_magnitude:
            self.image_magnitude = mpimg.imread(
                self.image_path_magnitude
            )  # Carrega a imagem
            messagebox.showinfo(
                "Imagem Selecionada",
                f"Imagem de Magnitude selecionada: {self.image_path_magnitude}",
            )

    def select_image_phase(self):
        """
        Carrega a imagem de fase selecionada pelo usuário e a atribui à variável self.image_phase.
        """
        self.image_path_phase = filedialog.askopenfilename(
            filetypes=[("Image files", ".png;.jpg;*.jpeg")])
        if self.image_path_phase:
            self.image_phase = mpimg.imread(
                self.image_path_phase)  # Carrega a imagem
            messagebox.showinfo(
                "Imagem Selecionada", f"Imagem de Fase selecionada: {self.image_path_phase}")

    def process_automatic(self):
        if not self.image_path_magnitude or not self.image_path_phase:
            messagebox.showerror("Erro", "Por favor, selecione ambas as imagens de magnitude e fase.")
            print("Erro: Imagens não selecionadas.")
            return

        try:
            # Validar x_min e x_max
            self.x_min = float(self.entries["x_min"].get())
            self.x_max = float(self.entries["x_max"].get())
            print(f"x_min: {self.x_min}, x_max: {self.x_max}")
        except ValueError:
            messagebox.showerror("Erro", "Insira valores numéricos válidos para os limites de frequência.")
            print("Erro: x_min ou x_max inválido.")
            return

        if self.x_min >= self.x_max:
            messagebox.showerror("Erro", "x_min deve ser menor que x_max.")
            print("Erro: x_min é maior ou igual a x_max.")
            return

        print(f"Processando imagens automaticamente com frequência de {self.x_min} Hz a {self.x_max} Hz...")

        try:
            # Processar imagens de magnitude e fase
            print("Chamando processamento de magnitude...")
            processed_image_magnitude, refined_curves_magnitude = image_processing.process_graph(
                self.image_path_magnitude, graph_type="bode"
            )
            print("Chamando processamento de fase...")
            processed_image_phase, refined_curves_phase = image_processing.process_graph(
                self.image_path_phase, graph_type="bode"
            )

            # Validar processamento
            if processed_image_magnitude is None or processed_image_phase is None:
                raise ValueError("Erro ao processar imagens. Verifique os arquivos selecionados.")

            print("Processamento concluído. Iniciando exibição...")

            # Salvar resultados do processamento
            self.processed_image_magnitude = processed_image_magnitude
            self.refined_curves_magnitude = refined_curves_magnitude
            self.processed_image_phase = processed_image_phase
            self.refined_curves_phase = refined_curves_phase

            # Exibir interface de anotação
            self.start_annotation_bode(
                self.processed_image_magnitude, self.refined_curves_magnitude,
                self.processed_image_phase, self.refined_curves_phase
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro no processamento automático: {e}")
            print(f"Erro no processamento automático: {e}")
    def create_interface_bode(self):
        """
        Cria os botões e ferramentas de interação para o gráfico de anotação.
        """
        print("Criando interface para anotação do gráfico de Bode...")

        button_style = {'hovercolor': 'lightblue'}

        # Botão para Marcar Pontos
        ax_points = plt.axes([0.1, 0.92, 0.12, 0.05])
        self.btn_points = Button(ax_points, "Marcar Pontos", color='lightgray', **button_style)
        self.btn_points.on_clicked(self.set_mode_points_bode)

        # Botão para Desenhar Linha
        ax_trace = plt.axes([0.25, 0.92, 0.12, 0.05])
        self.btn_trace = Button(ax_trace, "Desenhar Linha", color='lightgray', **button_style)
        self.btn_trace.on_clicked(self.set_mode_trace_bode)

        # Botão para Resetar Anotações
        ax_reset = plt.axes([0.4, 0.92, 0.1, 0.05])
        self.btn_reset = Button(ax_reset, "Resetar", color='lightgray', **button_style)
        self.btn_reset.on_clicked(self.reset_annotations_bode)

        # Botão para Salvar Anotações
        ax_save = plt.axes([0.55, 0.92, 0.1, 0.05])
        self.btn_save = Button(ax_save, "Salvar", color='green', **button_style)
        self.btn_save.on_clicked(self.save_curves_bode)

        # Seletores de Cor
        ax_colors = plt.axes([0.85, 0.75, 0.08, 0.2])
        self.radio_colors = RadioButtons(
            ax_colors, ["vermelho", "azul", "verde", "laranja", "rosa"], activecolor='black')
        self.radio_colors.on_clicked(self.set_color)


    def start_annotation_bode(self, processed_image_magnitude=None, refined_curves_magnitude=None,
                              processed_image_phase=None, refined_curves_phase=None):
        print("Iniciando anotação Bode...")

        self.annotation_root = ctk.CTk()
        self.annotation_root.title("Anotação dos Gráficos Bode")
        self.annotation_root.geometry("1200x800")
        self.annotation_root.resizable(True, True)

        # Configuração da figura e dos eixos
        self.fig, (self.ax_magnitude, self.ax_phase) = plt.subplots(
            2, 1, figsize=(10, 10))

        # Exibir o gráfico de magnitude
        if processed_image_magnitude is not None:
            self.ax_magnitude.imshow(
                processed_image_magnitude, cmap='gray', origin='upper', aspect='equal')
            for curve in refined_curves_magnitude:
                self.ax_magnitude.plot(
                    curve[:, 0], curve[:, 1], "-", color="red", linewidth=1)
        elif self.image_magnitude is not None:
            self.ax_magnitude.imshow(
                self.image_magnitude, cmap='gray', origin='upper', aspect='equal')

        self.ax_magnitude.set_title("Anotação do Gráfico de Magnitude")
        self.ax_magnitude.set_xlabel(
            f"Frequência (Hz), de {self.x_min} a {self.x_max}")
        self.ax_magnitude.set_ylabel("Magnitude (dB)")

        # Exibir o gráfico de fase
        if processed_image_phase is not None:
            self.ax_phase.imshow(processed_image_phase,
                                 cmap='gray', origin='upper', aspect='equal')
            for curve in refined_curves_phase:
                self.ax_phase.plot(
                    curve[:, 0], curve[:, 1], "-", color="blue", linewidth=1)
        elif self.image_phase is not None:
            self.ax_phase.imshow(self.image_phase, cmap='gray',
                                 origin='upper', aspect='equal')

        self.ax_phase.set_title("Anotação do Gráfico de Fase")
        self.ax_phase.set_xlabel(
            f"Frequência (Hz), de {self.x_min} a {self.x_max}")
        self.ax_phase.set_ylabel("Fase (graus)")

        # Configurar canvas e ferramentas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.annotation_root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        toolbar_frame = ctk.CTkFrame(self.annotation_root)
        toolbar_frame.pack(side=ctk.TOP, fill=ctk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

        # Criar interface de anotação
        self.create_interface_bode()
        self.connect_events_bode()

        back_button = ctk.CTkButton(self.annotation_root, text="Voltar", font=("Manrope", 16),
                                    command=self.on_closing_annotation)
        back_button.pack(pady=10)

        self.annotation_root.protocol(
            "WM_DELETE_WINDOW", self.on_closing_annotation)
        self.annotation_root.mainloop()

    def reset_annotations_bode(self, event):
        print("Resetando anotações Bode...")
        self.curves_magnitude = {}
        self.curves_phase = {}

        # Resetar gráfico de magnitude
        self.ax_magnitude.clear()
        if self.processed_image_magnitude is not None:
            self.ax_magnitude.imshow(
                self.processed_image_magnitude, cmap='gray', origin='upper', aspect='equal')
        elif self.image_magnitude is not None:
            self.ax_magnitude.imshow(
                self.image_magnitude, cmap='gray', origin='upper', aspect='equal')

        self.ax_magnitude.set_title("Anotação do Gráfico de Magnitude")
        self.ax_magnitude.set_xlabel(
            f"Frequência (Hz), de {self.x_min} a {self.x_max}")
        self.ax_magnitude.set_ylabel("Magnitude (dB)")
        self.ax_magnitude.grid(False)

        # Resetar gráfico de fase
        self.ax_phase.clear()
        if self.processed_image_phase is not None:
            self.ax_phase.imshow(self.processed_image_phase,
                                 cmap='gray', origin='upper', aspect='equal')
        elif self.image_phase is not None:
            self.ax_phase.imshow(self.image_phase, cmap='gray',
                                 origin='upper', aspect='equal')

        self.ax_phase.set_title("Anotação do Gráfico de Fase")
        self.ax_phase.set_xlabel(
            f"Frequência (Hz), de {self.x_min} a {self.x_max}")
        self.ax_phase.set_ylabel("Fase (graus)")
        self.ax_phase.grid(False)

        self.canvas.draw()
        print("Anotações resetadas.")

    def set_color(self, label):
        """
        Define a cor atual para anotação com base na seleção do usuário.
        """
        color_mapping = {
            "vermelho": "red",
            "azul": "blue",
            "verde": "green",
            "laranja": "orange",
            "rosa": "pink"
        }
        self.current_color = color_mapping.get(label, "red")
        print(f"Cor selecionada: {self.current_color}")

    def on_click_bode(self, event):
        """
        Lida com cliques do usuário nos gráficos de magnitude e fase.
        """
        if event.inaxes == self.ax_magnitude:
            print(
                f"Cliques no gráfico de magnitude: {event.xdata}, {event.ydata}")
            if self.mode == "points_bode":
                if self.current_color not in self.curves_magnitude:
                    self.curves_magnitude[self.current_color] = []
                self.curves_magnitude[self.current_color].append(
                    (event.xdata, event.ydata))
                self.ax_magnitude.plot(
                    event.xdata, event.ydata, "o", color=self.current_color)
                self.canvas.draw()
            elif self.mode == "trace_bode":
                if not self.trace_active:
                    self.trace_active = True
                    self.current_curve = [(event.xdata, event.ydata)]
                else:
                    self.trace_active = False
                    self.curves_magnitude.setdefault(
                        self.current_color, []).extend(self.current_curve)
                    x_coords, y_coords = zip(*self.current_curve)
                    self.ax_magnitude.plot(
                        x_coords, y_coords, "-", color=self.current_color)
                    self.canvas.draw()
                    self.current_curve = []

        elif event.inaxes == self.ax_phase:
            print(f"Cliques no gráfico de fase: {event.xdata}, {event.ydata}")
            if self.mode == "points_bode":
                if self.current_color not in self.curves_phase:
                    self.curves_phase[self.current_color] = []
                self.curves_phase[self.current_color].append(
                    (event.xdata, event.ydata))
                self.ax_phase.plot(event.xdata, event.ydata,
                                   "o", color=self.current_color)
                self.canvas.draw()
            elif self.mode == "trace_bode":
                if not self.trace_active:
                    self.trace_active = True
                    self.current_curve = [(event.xdata, event.ydata)]
                else:
                    self.trace_active = False
                    self.curves_phase.setdefault(
                        self.current_color, []).extend(self.current_curve)
                    x_coords, y_coords = zip(*self.current_curve)
                    self.ax_phase.plot(x_coords, y_coords,
                                       "-", color=self.current_color)
                    self.canvas.draw()
                    self.current_curve = []

    def on_motion_bode(self, event):
        """
        Lida com movimentos do mouse nos gráficos de magnitude e fase
        durante o modo de traçado (trace_bode).
        """
        if event.inaxes == self.ax_magnitude and self.mode == "trace_bode" and self.trace_active:
            self.current_curve.append((event.xdata, event.ydata))
            self.ax_magnitude.plot(
                event.xdata, event.ydata, ".", color=self.current_color)
            self.canvas.draw()
        elif event.inaxes == self.ax_phase and self.mode == "trace_bode" and self.trace_active:
            self.current_curve.append((event.xdata, event.ydata))
            self.ax_phase.plot(event.xdata, event.ydata,
                               ".", color=self.current_color)
            self.canvas.draw()

    def connect_events_bode(self):
        self.cid_click_magnitude = self.fig.canvas.mpl_connect(
            "button_press_event", self.on_click_bode)
        self.cid_motion_magnitude = self.fig.canvas.mpl_connect(
            "motion_notify_event", self.on_motion_bode)

    def on_motion_bode(self, event):
        """
        Lida com movimentos do mouse nos gráficos de magnitude e fase
        durante o modo de traçado (trace_bode).
        """
        if event.inaxes == self.ax_magnitude and self.mode == "trace_bode" and self.trace_active:
            self.current_curve.append((event.xdata, event.ydata))
            self.ax_magnitude.plot(
                event.xdata, event.ydata, ".", color=self.current_color)
            self.canvas.draw()
        elif event.inaxes == self.ax_phase and self.mode == "trace_bode" and self.trace_active:
            self.current_curve.append((event.xdata, event.ydata))
            self.ax_phase.plot(event.xdata, event.ydata,
                               ".", color=self.current_color)
            self.canvas.draw()

    def set_mode_points_bode(self, event):
        self.mode = "points_bode"
        print("Modo: Marcar Pontos Bode")

    def set_mode_trace_bode(self, event):
        self.mode = "trace_bode"
        self.current_curve = []
        self.trace_active = False
        print("Modo: Desenhar Linha Bode")

    def save_curves_bode(self, event):
        print("Salvando anotações Bode...")
        all_data_magnitude = []
        all_data_phase = []
        for color, points in self.curves_magnitude.items():
            for x, y in points:
                all_data_magnitude.append({"Color": color, "X": x, "Y": y})
        for color, points in self.curves_phase.items():
            for x, y in points:
                all_data_phase.append({"Color": color, "X": x, "Y": y})

        if not all_data_magnitude and not all_data_phase:
            print("Nenhuma anotação para salvar.")
            return

        if all_data_magnitude:
            df_magnitude = pd.DataFrame(all_data_magnitude)
            output_path_magnitude = filedialog.asksaveasfilename(
                defaultextension="_magnitude.csv", filetypes=[("CSV files", "*.csv")])
            if output_path_magnitude:
                df_magnitude.to_csv(output_path_magnitude, index=False)
                print(
                    f"Anotações de Magnitude salvas em {output_path_magnitude}")

        if all_data_phase:
            df_phase = pd.DataFrame(all_data_phase)
            output_path_phase = filedialog.asksaveasfilename(
                defaultextension="_phase.csv", filetypes=[("CSV files", "*.csv")])
            if output_path_phase:
                df_phase.to_csv(output_path_phase, index=False)
                print(f"Anotações de Fase salvas em {output_path_phase}")

    def reset_annotations_bode(self, event):
        print("Resetando anotações Bode...")
        self.curves_magnitude = {}
        self.curves_phase = {}

        # Resetar gráfico de magnitude
        self.ax_magnitude.clear()
        if self.processed_image_magnitude is not None:
            self.ax_magnitude.imshow(
                self.processed_image_magnitude, cmap='gray', origin='upper', aspect='equal')
        elif self.image_magnitude is not None:
            self.ax_magnitude.imshow(
                self.image_magnitude, cmap='gray', origin='upper', aspect='equal')

        self.ax_magnitude.set_title("Anotação do Gráfico de Magnitude")
        self.ax_magnitude.set_xlabel(
            f"Frequência (Hz), de {self.x_min} a {self.x_max}")
        self.ax_magnitude.set_ylabel("Magnitude (dB)")
        self.ax_magnitude.grid(False)

        # Resetar gráfico de fase
        self.ax_phase.clear()
        if self.processed_image_phase is not None:
            self.ax_phase.imshow(self.processed_image_phase,
                                 cmap='gray', origin='upper', aspect='equal')
        elif self.image_phase is not None:
            self.ax_phase.imshow(self.image_phase, cmap='gray',
                                 origin='upper', aspect='equal')

        self.ax_phase.set_title("Anotação do Gráfico de Fase")
        self.ax_phase.set_xlabel(
            f"Frequência (Hz), de {self.x_min} a {self.x_max}")
        self.ax_phase.set_ylabel("Fase (graus)")
        self.ax_phase.grid(False)

        self.canvas.draw()
        print("Anotações resetadas.")

    def on_closing(self):
        if self.root is not None:
            self.root.destroy()
            self.root = None

    def on_closing_annotation(self):
        if self.annotation_root is not None:
            self.annotation_root.destroy()
            self.annotation_root = None
