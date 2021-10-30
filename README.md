<h1 align="center">2202_NCMF</h1>

# Project Description
This tool is designed to provide translation of Speech to Text and Image to Text. It is a simple to use tool and can be use by anyone.

*Note: Pydub is used for the conversion of different extension to .wav & it uses FFMPEG, a framework to capture, decode, mainipulate

# Installation Guide for Dependencies
1. pip install SpeechRecognition
2. pip install pydub (for the conversion of different extension to .wav)
3. Installed the FFMPEG zip file in your computer (Windows) || run command: sudo apt-get install ffmpeg (Linux)

Follow this tutorial for the pydub set up [Refer to Pooja Mallam's Answer] [only need to follow until step 4; ignore step 5] & restart your IDE
https://stackoverflow.com/questions/3049572/how-to-convert-mp3-to-wav-in-python#comment3122106_3049572

How to run the py file in terminal will just be: python stt.py -f (filename) 
Eg: python stt.py -f welcome.mp3 --> they will convert and save results as text file

Reference for the stt.py so far
1. https://github.com/jiaaro/pydub/blob/master/API.markdown - pydub is used to help with the conversion of audio files to wav 
2. https://sonsuzdesign.blog/2020/08/14/speech-recognition-in-python-the-complete-beginners-guide/ & https://realpython.com/python-speech-recognition/#the-recognizer-class & https://www.thepythoncode.com/article/using-speech-recognition-to-convert-speech-to-text-python - Used to perform the speech recognition portion for 'smaller' audio files 

1. Install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki *Take note of the installation path
2. Add Tesseract installation path to your computer System Environment path
3. pip install opencv-python   
4. pip install pytesseract


# How to Use

# Built With 
- Python

*This project is done by a group of SIT (Singapore Institute of Technology) Information Security Year 2 Students. 
**Chong Fu Min**

**Crystal Choo Jia Xian**

**Marissa Krystle Tambou**

**Nicole Tan Yi Jing**
