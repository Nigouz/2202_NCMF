# 2202_NCMF
Just in case we need to update one another regarding our tool

For SpeechRecognition I had to install this in my VSCODE IDE Terminal
1. pip install SpeechRecognition
And also installed the FFMPEG zip file in my computer for pydub to work
Follow this tutorial for the pydub set up [Refer to Pooja Mallam's Answer] & restart your IDE (idk if others work, but for VSCODE, it has to be restarted after his steps)
2. https://stackoverflow.com/questions/3049572/how-to-convert-mp3-to-wav-in-python#comment3122106_3049572

How to run the py file in terminal will just be: python stt.py -f (filename) 
Eg: python stt.py -f welcome.mp3 --> they will convert and save results as text file

Let me know if there are other issues. 

Reference for the stt.py so far
1. https://github.com/jiaaro/pydub/blob/master/API.markdown - pydub is used to help with the conversion of audio files to wav 
2. https://sonsuzdesign.blog/2020/08/14/speech-recognition-in-python-the-complete-beginners-guide/ & https://realpython.com/python-speech-recognition/#the-recognizer-class & https://www.thepythoncode.com/article/using-speech-recognition-to-convert-speech-to-text-python- Used to perform the speech recognition portion for 'smaller' audio files 
