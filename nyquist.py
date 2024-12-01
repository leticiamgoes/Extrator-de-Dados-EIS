import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import Button, RadioButtons
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.image as mpimg
import image_processing
import annotation_loader  # Importar annotation_loader para o uso do LabelMe
import numpy as np



class NyquistAnnotationApp:
    def __init__(self, mode):
        self.image_path = None
        self.annotation_path = None
        self.x_min = 0
        self.x_max = 1
        self.y_min = 0
        self.y_max = 1
        self.curves = {}
        self.current_curve = []
        self.trace_active = False
        self.current_color = "red"
        self.mode = mode
        self.root = None
        self.annotation_root = None
        self.fig = None
        self.ax = None
        self.canvas = None
        self.toolbar = None

        self.launch_nyquist_screen()

    def launch_nyquist_screen(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Extrator de Dados - Nyquist Annotation Tool")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        title_label = ctk.CTkLabel(self.root, text="Ferramenta de Extração de Dados - Nyquist", font=("Manrope", 22, "bold"))
        title_label.pack(pady=20)

        select_image_button = ctk.CTkButton(self.root, text="Selecionar Imagem", font=("Manrope", 16), command=self.select_image)
        select_image_button.pack(pady=15)

        self.entries = {}
        frame_limits = ctk.CTkFrame(self.root)
        frame_limits.pack(pady=20, padx=40, fill="both", expand=True)
        limits = ["x_min", "x_max", "y_min", "y_max"]
        for limit in limits:
            label = ctk.CTkLabel(frame_limits, text=f"{limit}:", font=("Manrope", 14))
            label.grid(row=limits.index(limit), column=0, sticky="e", padx=10, pady=10)
            entry = ctk.CTkEntry(frame_limits, width=150, font=("Manrope", 14))
            entry.grid(row=limits.index(limit), column=1, padx=10, pady=10)
            self.entries[limit] = entry

        start_annotation_button = ctk.CTkButton(self.root, text="Iniciar Anotação", font=("Manrope", 16), command=self.process_limits_nyquist)
        start_annotation_button.pack(pady=20)

        back_button = ctk.CTkButton(self.root, text="Voltar", font=("Manrope", 16), command=self.on_closing)
        back_button.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def select_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", ".png;.jpg;*.jpeg")])
        if self.image_path:
            messagebox.showinfo("Imagem Selecionada", f"Imagem selecionada: {self.image_path}")

    def process_limits_nyquist(self):
        try:
            # Leia os valores dos inputs
            self.x_min = float(self.entries["x_min"].get())
            self.x_max = float(self.entries["x_max"].get())
            self.y_min = float(self.entries["y_min"].get())
            self.y_max = float(self.entries["y_max"].get())
        except ValueError:
            # Mostre uma mensagem de erro se os valores não forem válidos
            messagebox.showerror("Erro", "Insira valores numéricos válidos para os limites.")
            return
        if not self.image_path:
            messagebox.showerror("Erro", "Selecione uma imagem antes de continuar.")
            return

        self.on_closing()
        self.start_annotation_nyquist()



    def start_annotation_nyquist(self):
        print(f"Iniciando anotação Nyquist no modo {self.mode}...")
        self.annotation_root = ctk.CTk()
        self.annotation_root.title("Anotação do Gráfico Nyquist")
        self.annotation_root.geometry("1200x800")
        self.annotation_root.resizable(True, True)

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.image = mpimg.imread(self.image_path)

        if self.mode == "automatic":
            processed_image = image_processing.preprocess_image(self.image_path)
            image_cleaned = image_processing.remove_text_and_symbols(processed_image)
            image_without_grid = image_processing.remove_grid_lines(image_cleaned)
            detected_curves = image_processing.segment_curves(image_without_grid)
            refined_curves = image_processing.refine_curves(detected_curves)

            self.ax.imshow(image_without_grid, cmap='gray', origin='upper', aspect='equal', 
                        extent=[self.x_min, self.x_max, self.y_min, self.y_max])

            self.curves = {f"curve_{i}": curve for i, curve in enumerate(refined_curves)}

            for curve in refined_curves:
                self.ax.plot(curve[:, 0], curve[:, 1], "-", color=self.current_color, linewidth=1)

        else:
            self.ax.imshow(self.image, cmap='gray', origin='upper', aspect='equal', 
                        extent=[self.x_min, self.x_max, self.y_min, self.y_max])

        self.ax.set_title("Anotação do Gráfico Nyquist")
        self.ax.set_xlabel(f"Real (Z), de {self.x_min} a {self.x_max}")
        self.ax.set_ylabel(f"Imag (Z), de {self.y_min} a {self.y_max}")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.annotation_root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.annotation_root)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        self.create_interface_nyquist()
        self.connect_events()

        back_button = ctk.CTkButton(self.annotation_root, text="Voltar", font=("Manrope", 16), command=self.on_closing_annotation)
        back_button.pack(pady=10)

        self.annotation_root.protocol("WM_DELETE_WINDOW", self.on_closing_annotation)
        self.annotation_root.mainloop()



    def create_interface_nyquist(self):
        button_style = {'hovercolor': 'lightblue'}

        ax_points = plt.axes([0.1, 0.90, 0.12, 0.05])
        self.btn_points = Button(ax_points, "Marcar Pontos", color='lightgray', **button_style)
        self.btn_points.on_clicked(self.set_mode_points)

        ax_trace = plt.axes([0.25, 0.90, 0.12, 0.05])
        self.btn_trace = Button(ax_trace, "Desenhar Linha", color='lightgray', **button_style)
        self.btn_trace.on_clicked(self.set_mode_trace)

        ax_eraser = plt.axes([0.40, 0.90, 0.12, 0.05])
        self.btn_eraser = Button(ax_eraser, "Borracha", color='lightgray', **button_style)
        self.btn_eraser.on_clicked(self.set_mode_eraser)

        ax_reset = plt.axes([0.55, 0.90, 0.12, 0.05])
        self.btn_reset = Button(ax_reset, "Resetar", color='lightgray', **button_style)
        self.btn_reset.on_clicked(self.reset_annotations_nyquist)

        ax_save = plt.axes([0.70, 0.90, 0.12, 0.05])
        self.btn_save = Button(ax_save, "Salvar", color='green', **button_style)
        self.btn_save.on_clicked(self.save_curves_nyquist)

        ax_colors = plt.axes([0.85, 0.75, 0.08, 0.2])
        self.radio_colors = RadioButtons(ax_colors, ["vermelho", "azul", "verde", "laranja", "rosa"], activecolor='black')
        self.radio_colors.on_clicked(self.set_color)

    def connect_events(self):
        self.cid_click = self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.cid_motion = self.fig.canvas.mpl_connect("motion_notify_event", self.on_motion)

    # Funções adicionais continuam as mesmas...
    def set_mode_eraser(self, event):
        self.mode = "eraser"
        print("Modo: Borracha")

    def set_mode_points(self, event):
        self.mode = "points"
        print("Modo: Marcar Pontos")

    def set_mode_trace(self, event):
        self.mode = "trace"
        self.current_curve = []
        self.trace_active = False
        print("Modo: Desenhar Linha")

    def set_color(self, label):
        color_mapping = {
            "vermelho": "red",
            "azul": "blue",
            "verde": "green",
            "laranja": "orange",
            "rosa": "pink",
            "preto": "black"
        }
        self.current_color = color_mapping.get(label, "red")
        print(f"Cor selecionada: {self.current_color}")

    def reset_annotations_nyquist(self, event):
        print("Resetando anotações Nyquist...")
        self.curves = {}
        self.ax.clear()
        self.ax.imshow(self.image, cmap='gray', origin='upper',
                       extent=[self.x_min, self.x_max, self.y_min, self.y_max],
                       aspect='equal')  # Manter a proporção fixa da imagem
        self.ax.set_title("Anotação do Gráfico Nyquist")
        self.ax.set_xlabel(f"Real (Z), de {self.x_min} a {self.x_max}")
        self.ax.set_ylabel(f"Imag (Z), de {self.y_min} a {self.y_max}")
        self.canvas.draw()
        print("Anotações resetadas.")

    def save_curves_nyquist(self, event):
        print("Salvando anotações Nyquist...")
        all_data = []
        for color, points in self.curves.items():
            for x, y in points:
                all_data.append({"Color": color, "X": x, "Y": y})
        if not all_data:
            print("Nenhuma anotação para salvar.")
            return
        df = pd.DataFrame(all_data)
        output_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if output_path:
            df.to_csv(output_path, index=False)
            print(f"Anotações salvas em {output_path}")
        else:
            print("Operação de salvamento cancelada.")

    def on_click(self, event):
        if event.inaxes != self.ax:
            return

        if self.mode == "eraser":
            # Apagar o ponto ou segmento mais próximo
            min_distance = float("inf")
            closest_point = None
            closest_curve_key = None

            for curve_key, points in self.curves.items():
                for point in points:
                    distance = np.sqrt((event.xdata - point[0]) ** 2 + (event.ydata - point[1]) ** 2)
                    if distance < min_distance:
                        min_distance = distance
                        closest_point = point
                        closest_curve_key = curve_key

            # Se encontrou um ponto próximo, remova-o
            if closest_point and min_distance < 10:  # Tolerância para o clique
                self.curves[closest_curve_key].remove(closest_point)
                print(f"Ponto apagado: {closest_point}")
                self.redraw_curves()  # Atualizar o gráfico
            else:
                print("Nenhum ponto próximo encontrado.")

        elif self.mode == "points":
            if self.current_color not in self.curves:
                self.curves[self.current_color] = []
            self.curves[self.current_color].append((event.xdata, event.ydata))
            self.ax.plot(event.xdata, event.ydata, "o", color=self.current_color)
            self.canvas.draw()
            print(f"Ponto marcado: ({event.xdata}, {event.ydata})")

        elif self.mode == "trace":
            if not self.trace_active:
                self.trace_active = True
                self.current_curve = [(event.xdata, event.ydata)]
                print("Traçado iniciado.")
            else:
                self.trace_active = False
                self.curves.setdefault(self.current_color, []).extend(self.current_curve)
                x_coords, y_coords = zip(*self.current_curve)
                self.ax.plot(x_coords, y_coords, "-", color=self.current_color)
                self.canvas.draw()
                self.current_curve = []
                print("Traçado finalizado e salvo.")
    def redraw_curves(self):
        # Limpa o eixo sem remover o fundo
        self.ax.clear()
        self.ax.imshow(self.image, cmap='gray', origin='upper', 
                    extent=[self.x_min, self.x_max, self.y_min, self.y_max])

        # Redesenha todas as curvas
        for color, points in self.curves.items():
            if points:
                x_coords, y_coords = zip(*points)
                self.ax.plot(x_coords, y_coords, "-", color=color, linewidth=1)
        
        self.canvas.draw()


    def on_motion(self, event):
        if event.inaxes != self.ax or self.mode != "trace" or not self.trace_active:
            return
        # Adicionar o ponto atual à curva em andamento
        self.current_curve.append((event.xdata, event.ydata))
        self.ax.plot(event.xdata, event.ydata, ".", color=self.current_color)
        self.canvas.draw()


    def on_closing(self):
        if self.root is not None:
            self.root.destroy()
            self.root = None

    def on_closing_annotation(self):
        if self.annotation_root is not None:
            self.annotation_root.destroy()
            self.annotation_root = None


if __name__ == "__main__":
    NyquistAnnotationApp("manual")
