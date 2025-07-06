# AI-shorts-generator
This project automates video creation using a Python/Flask backend. It orchestrates Gemini for scriptwriting, ElevenLabs for narration, and Pexels for visuals. FFmpeg then compiles these elements into a finished video, demonstrating a full generative AI workflow from a single prompt to a final product.

# 🤖 VidGen AI: Automated Video Creation Pipeline

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

An end-to-end AI pipeline that automatically generates short-form videos from a single prompt. It orchestrates multiple APIs for scriptwriting, narration, and video sourcing, then compiles everything into a finished product with FFmpeg.

<br>

https://github.com/YOUR_USERNAME/YOUR_REPO/assets/YOUR_USER_ID/d1a9e3b1-b9a6-4f4c-8b5e-0c1f2a3b4d5e

_Note: You should record a short screen capture of your app working, upload it to the issue section of your GitHub repo to get a URL, and replace the link above._

---

## ✨ About The Project

In the age of short-form content, the ability to produce engaging videos quickly is a massive advantage. This project was built to explore the complete automation of the video creation process, handling everything from the initial creative idea to the final rendered MP4.

This is not just a call to a single API; it's a full-stack application that manages a complex generative workflow, demonstrating how to build robust, practical AI-powered systems.

---

## 🚀 Key Features

-   **📝 AI-Powered Scriptwriting**: Leverages Google's Gemini Pro to generate unique scripts and titles for various niches (e.g., Horror Stories, Motivational Speeches, Historical Facts).
-   **🗣️ Lifelike Narration**: Integrates with ElevenLabs' API to produce high-quality, human-sounding text-to-speech audio for the script.
-   **🎞️ Automated Visuals**: Intelligently queries the Pexels API to find and download relevant, high-quality stock footage that matches keywords extracted by the AI.
-   **🎬 Intelligent Compilation**: Uses FFmpeg to automatically:
    -   Combine and edit video clips to match the narration length.
    -   Overlay the narration track.
    -   Mix in appropriate background music based on the video's mood.
    -   Standardize the output to 720p HD resolution.
-   **🌐 Simple Web Interface**: Built with Flask to provide an easy-to-use interface for starting the generation process.

---

## 🛠️ Tech Stack & Architecture

This project is built with a powerful combination of modern AI services and robust backend technologies.

| Tech                                                                   | Description                                |
| ---------------------------------------------------------------------- | ------------------------------------------ |
| **Python & Flask** | Core backend language and web framework.   |
| **Google Gemini API** | For AI scriptwriting and keyword extraction. |
| **ElevenLabs API** | For generating high-quality voiceovers.      |
| **Pexels API** | For sourcing royalty-free stock videos.    |
| **FFmpeg** | The powerhouse for all video/audio processing and compilation. |
| **HTML/CSS/JS** | For the simple frontend interface.         |

### System Architecture

The application follows a sequential pipeline to generate the video:

```
[User Selects Niche] -> [Flask Backend]
      |
      v
[1. Gemini API] -> Generates {Script, Title, Keywords}
      |
      v
[2. ElevenLabs API] -> Generates narration.mp3 from Script
      |
      v
[3. Pexels API] -> Downloads video clips based on Keywords
      |
      v
[4. FFmpeg] -> Compiles clips + audio + music -> final_video.mp4
      |
      v
[Returns Video to User]
```

---

## 🏁 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

Before you begin, ensure you have the following installed:
* **Python 3.8+**
* **FFmpeg**: You must have FFmpeg installed on your system and accessible from the command line. You can download it from [ffmpeg.org](https://ffmpeg.org/download.html).
* **API Keys**:
    * Google Gemini API
    * ElevenLabs API
    * Pexels API

### Installation & Setup

1.  **Clone the Repository**
    ```sh
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPO.git](https://github.com/YOUR_USERNAME/YOUR_REPO.git)
    cd YOUR_REPO
    ```

2.  **Create a Virtual Environment (Recommended)**
    ```sh
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**
    Create a file named `.env` in the root directory of the project. Copy the contents of `.env.example` (if you have one) or add the following lines, replacing the placeholder text with your actual API keys:
    ```.env
    PEXELS_API_KEY='Your_Pexels_API_Key_Here'
    GEMINI_API_KEY='Your_Gemini_API_Key_Here'
    ELEVENLABS_API_KEY='Your_ElevenLabs_API_Key_Here'
    ```

5.  **Run the Application**
    ```sh
    flask run
    ```
    Open your web browser and navigate to `http://127.0.0.1:5000` to use the application.

---

## 💡 Usage

Once the application is running, simply:
1.  Open your browser to the local server address.
2.  Select a video niche from the dropdown menu.
3.  Click the "Generate Video" button.
4.  Wait for the process to complete (you can monitor the progress in your terminal). The final video will appear on the page once it's ready.

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🙏 Acknowledgments

* [Google AI](https://ai.google/) for the powerful Gemini model.
* [ElevenLabs](https://elevenlabs.io/) for their state-of-the-art voice generation.
* [Pexels](https://www.pexels.com) for providing high-quality, free stock photos and videos.
* [FFmpeg](https://ffmpeg.org/) - The essential tool for any multimedia manipulation.

```
