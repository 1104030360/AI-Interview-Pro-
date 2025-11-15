# Project Overview

This project is a real-time emotion and presence detection system designed for the service industry. It uses computer vision to analyze video streams from two cameras (representing a customer and a server) to determine their emotions and whether they are present. The system then generates reports, including emotion wave graphs and sentiment analysis bar charts. A web interface is available to display these reports.

The project is primarily built with Python and leverages several libraries for its core functionalities:
- **OpenCV**: For capturing and processing video streams.
- **DeepFace**: For emotion, age, and gender analysis.
- **Keras/TensorFlow**: For running a pre-trained model to detect presence.
- **Matplotlib**: For generating charts and graphs of the analysis results.
- **Flask**: For serving a web-based report of the findings.
- **FFmpeg**: For video format conversion.

## How to Run the Project

1.  **Install Dependencies:**
    Make sure you have Python installed. Then, install the required libraries using pip:
    ```bash
    pip install keras opencv-python numpy deepface pillow matplotlib flask ffmpeg-python
    ```

2.  **Run the Emotion Analysis:**
    The main entry point for the analysis is `Auto_Switch.py`. This script will first detect if a person is present in front of the camera and then trigger the main analysis script `project.py`.
    ```bash
    python Auto_Switch.py
    ```
    The analysis will start when a person is detected for a few seconds. The script uses two cameras. To stop the analysis, press the 'q' key.

3.  **View the Report:**
    The project includes a Flask application to display the analysis results. To run the web server:
    ```bash
    python report_main.py
    ```
    Then, open your web browser and navigate to `http://127.0.0.1:5000` to see the report.

## Key Files

-   `Auto_Switch.py`: The entry point of the application. It detects the presence of a person and starts the main analysis.
-   `project.py`: The core script that performs emotion, age, and gender analysis using two cameras. It saves the analysis results as images and videos.
-   `report_main.py`: A Flask web server that displays the analysis results in an HTML report.
-   `report2.html`, `report.CSS`, `report.JS`: The frontend files for the web report.
-   `haarcascade_frontalface_default.xml`: The Haar cascade file used for face detection with OpenCV.
-   `keras_model.h5` and `labels.txt`: The pre-trained Keras model and corresponding labels for presence detection.
-   `*.jpg`: The output images from the analysis, including emotion wave and bar charts.
-   `*.mp4`: The output video recordings from the cameras.
