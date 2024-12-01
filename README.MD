# Nyquist/Bode Annotation Tool

## Overview

This application provides a robust and interactive tool for extracting data from Nyquist and Bode plots. Users can annotate these graphs either manually or automatically, enabling efficient analysis and data processing for impedance spectroscopy.

## Features

1. **Nyquist Plot Annotation**:
   - Manual mode: Users can mark points, draw lines, and erase annotations directly.
   - Automatic mode: Processes the graph to extract and refine curves.

2. **Bode Plot Annotation**:
   - Magnitude and phase images can be analyzed separately.
   - Supports both manual and automatic modes for flexible interaction.

3. **Image Processing**:
   - Preprocesses images to enhance contrast and reduce noise.
   - Removes gridlines, text, and symbols for clean data extraction.
   - Segments and refines curves for accurate analysis.

4. **Graph Interactivity**:
   - Intuitive graphical interface for marking points and drawing curves.
   - Allows customization of curve colors and erasing of specific data points.

5. **Output**:
   - Saves annotations in CSV format for easy integration into other analysis tools.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/nyquist-bode-tool.git
   cd nyquist-bode-tool
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure you have Python 3.8+ installed.

## Usage

1. Run the main application:
   ```bash
   python app.py
   ```

2. Choose the plot type:
   - **Nyquist**
   - **Bode**

3. Select the annotation mode:
   - **Manual**: Interact directly with the plot.
   - **Automatic**: Let the tool process and extract curves automatically.

4. Follow the on-screen instructions to load images and annotate.

5. Save annotations in CSV format for further use.

## Dependencies

- `customtkinter`: For creating the graphical user interface.
- `matplotlib`: For plotting and annotating graphs.
- `opencv-python`: For image preprocessing.
- `scipy`: For curve refinement using splines.
- `numpy`: For numerical computations.
- `pandas`: For exporting data annotations.

## File Structure

- `app.py`: Main application that integrates Nyquist and Bode functionalities.
- `nyquist.py`: Handles Nyquist plot annotations.
- `bode.py`: Handles Bode plot annotations.
- `image_processing.py`: Contains all image preprocessing and curve refinement logic.
- `gui.py`: GUI logic for the tool.

## Contributing

Contributions are welcome! If you'd like to enhance this project, feel free to fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.

## Support

If you encounter any issues or have questions, please open an issue in the GitHub repository or contact the maintainers.