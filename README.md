# Documentation for YouTube Video Processing and Meeting Minutes Generator

## Overview

This application processes YouTube videos to transcribe the audio, generate meeting minutes, and interactively display this information on a Streamlit web interface. It extracts abstract summaries, key points, and action items from the transcribed text, and offers interactive features for user engagement with the AI-generated content.

## Installation

### Prerequisites

- Python 3.x
- Streamlit
- OpenAI API key

### Dependencies

Install the required libraries using pip:

```bash
pip install openai streamlit python-dotenv langchain-community youtube-dl python-docx
```


# Environment Setup
1. Obtain an API key from OpenAI.

2. Create a .env file in the project root and add your OpenAI API key:

    ```plaintext
    OPENAI_API_KEY=your_openai_api_key_here
    ```
3. Load the environment variables in your script by calling load_dotenv().

# Application Functions

## transcribe_audio(audio_file_path)
Transcribes audio content from a specified file using OpenAI's Whisper model.

- Parameters:
    - audio_file_path: Path to the audio file.
- Returns:

    - The transcribed text as a string.

## abstract_summary_extraction(transcription)
Generates an abstract summary from the provided transcription.

- Parameters:
    - transcription: The text of the transcription.
- Returns:

    - An abstract summary as a string.


## key_points_extraction(transcription)
Identifies key points from the transcription.

- Parameters:
    - transcription: The text of the transcription.
- Returns:

    - A string listing the key points.

## action_item_extraction(transcription)
Extracts actionable items from the transcription.

- Parameters:

    - transcription: The text of the transcription.
- Returns:
    - A string listing the action items.

## meeting_minutes(transcription)
Combines the outputs of abstract summary, key points, and action item extractions into a structured format.

- Parameters:

    - transcription: The text of the transcription.
- Returns:
-   A dictionary with the abstract summary, key points, and action items.
## save_as_docx(minutes, filename)
Saves the meeting minutes into a DOCX file.

- Parameters:

    - minutes: Dictionary containing meeting minutes sections.
    - filename: Desired filename for the DOCX document.
## process_youtube_video(url)
Processes a YouTube video URL to extract and transcribe audio, then generates meeting minutes.

- Parameters:
    - url: YouTube video URL.
- Returns:
    - Transcription text, meeting minutes dictionary, and DOCX filename.
Streamlit UI Components

This section of the script initializes and manages the Streamlit user interface, facilitating user interaction with the video processing and meeting minutes features. It includes text inputs, video displays, expanders for content display, and chat functionality for dynamic interaction with the AI