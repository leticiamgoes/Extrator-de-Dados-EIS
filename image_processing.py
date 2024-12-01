import cv2
import numpy as np
from scipy.interpolate import splprep, splev


def preprocess_image(image_path, graph_type="generic"):
    try:
        # Carregar a imagem em escala de cinza
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError(f"Erro ao carregar a imagem: {image_path}")

        # Melhorar contraste
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced_image = clahe.apply(image)

        # Reduzir ruído
        blurred_image = cv2.medianBlur(enhanced_image, 5)

        if graph_type == "bode":
            # Ajustar thresholds dinamicamente para gráficos de Bode
            median = np.median(blurred_image)
            lower_thresh = int(max(0, 0.4 * median))
            upper_thresh = int(min(255, 1.2 * median))
        else:
            # Ajustes para gráficos genéricos ou Nyquist
            lower_thresh, upper_thresh = 50, 150

        # Detectar bordas
        edges = cv2.Canny(blurred_image, lower_thresh, upper_thresh)

        # Fechar arestas desconectadas
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)

        return closed_edges
    except Exception as e:
        print(f"Erro no pré-processamento da imagem: {e}")
        return None


def remove_text_and_symbols(image, graph_type="generic"):
    try:
        # Detectar contornos para identificar símbolos ou ruídos
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        mask = np.zeros_like(image)
        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if 10 < area < 800:  # Faixa de áreas para símbolos pequenos
                circularity = (4 * np.pi * area) / (perimeter**2 + 1e-5)
                if circularity > 0.7:  # Alta circularidade = símbolos
                    cv2.drawContours(mask, [contour], -1, 255, -1)

        image_cleaned = cv2.bitwise_and(image, cv2.bitwise_not(mask))
        return image_cleaned
    except Exception as e:
        print(f"Erro ao remover símbolos e ruídos: {e}")
        return image


def remove_grid_lines(image, graph_type="generic"):
    try:
        edges = cv2.Canny(image, 50, 150, apertureSize=3)

        if graph_type == "bode":
            # Detecção de linhas ajustada para gráficos de Bode
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=30, maxLineGap=10)
        else:
            # Configurações padrão (ex.: gráficos Nyquist)
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=5)

        mask = np.zeros_like(image)
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(mask, (x1, y1), (x2, y2), 255, 2)

        image_without_grid = cv2.bitwise_and(image, cv2.bitwise_not(mask))
        return image_without_grid
    except Exception as e:
        print(f"Erro ao remover linhas da malha: {e}")
        return image


def segment_curves(image):
    try:
        _, binary_image = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        curves = [c for c in contours if cv2.contourArea(c) > 200]
        return curves
    except Exception as e:
        print(f"Erro na segmentação das curvas: {e}")
        return []


def refine_curves(curves):
    try:
        refined_curves = []
        for contour in curves:
            x = contour[:, 0, 0]
            y = contour[:, 0, 1]

            # Ajustar spline para suavizar curvas
            tck, _ = splprep([x, y], s=0.01)
            u = np.linspace(0, 1, 1000)
            x_smooth, y_smooth = splev(u, tck)

            refined_curves.append(np.array([x_smooth, y_smooth]).T)
        return refined_curves
    except Exception as e:
        print(f"Erro no refinamento das curvas: {e}")
        return []

def process_graph(image_path, graph_type="bode"):
    try:
        print(f"Processando imagem: {image_path}")
        processed_image = preprocess_image(image_path, graph_type)
        if processed_image is None:
            raise ValueError("Erro ao pré-processar a imagem.")

        print("Removendo textos e símbolos...")
        image_cleaned = remove_text_and_symbols(processed_image, graph_type)

        print("Removendo linhas da grade...")
        image_without_grid = remove_grid_lines(image_cleaned, graph_type)

        print("Segmentando curvas...")
        detected_curves = segment_curves(image_without_grid)
        print(f"Curvas detectadas: {len(detected_curves)}")

        print("Refinando curvas...")
        refined_curves = refine_curves(detected_curves)

        if not refined_curves:
            print("Nenhuma curva refinada encontrada.")
            return None, None

        print("Processamento concluído com sucesso.")
        return image_without_grid, refined_curves
    except Exception as e:
        print(f"Erro no processamento do gráfico: {e}")
        return None, None


