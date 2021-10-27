import speech_recognition as sr
import os, mimetypes, argparse
from argparse import ArgumentParser
from pydub import AudioSegment

def arg_parser():
    parser = ArgumentParser(description="Testing 123")
    parser.add_argument('-f', type=argparse.FileType('r'), required=True, help= "Specify audio file for conversion") #Argparse.filetype (r) is just to specify to READ the file"""
    parser.add_argument("-d", type= open, help="Specify Disc Image Files to extract audio files and perform conversion on") #Untouched yet, only focusing on -f now
    return parser.parse_args()
    
def file_checker():
    arg = arg_parser() #So that we can use the variables from arg_parser function

    #if user argument specified -f , check for file extension 
    if arg.f:
        path = os.path.realpath(arg.f.name) #to get file path 
        name, ext = os.path.splitext(path) #to obtain file name and file extension
        
        #check if file is audio file (MP3)
        #make checking 'case-insenstive' so lower them all first
        ext.lower()

        #If file is not wav file, perform conversion first before calling text conversion func                                                           
        if ext =='.mp3':
            mp3file = AudioSegment.from_mp3(arg.f.name)
            result = mp3file.export("converted.wav", format="wav")
            converter(result)
        
        if ext =='.ogg':
            
            oggfile = AudioSegment.from_file(arg.f.name)
            result = oggfile.export("converted.wav", format="wav")
            converter(result)

        #Speech Recognition only runs with .wav files, so if its already .wav, no conversion has to be done, we can begin the speech recognition
        if ext == '.wav':
            converter(arg.f.name)
                
        #if ext do not exists, guess file ext (Have not tried this portion)
        possible = mimetypes.guess_extension(path)
        if not ext:
            if possible == '.wav' or ext == '.mp3':
                print('Yeah guess')
    

#Function that does the conversion with Google API (Limitation: Can only convert up to 60 minutes)
def converter(audiofile):
    r = sr.Recognizer()
    with sr.AudioFile(audiofile) as src:
        #listen for data
        audio=r.record(src)
        #convert speech to text
        text=r.recognize_google(audio)
        
        #write the text into a file for viewing
        with open('text.txt','w') as textfile:
            for x in text:
                textfile.write(x)

def main():
    arguments= arg_parser()
    file_checker()

if __name__ == "__main__":
    main()


### For my own references ###
#Initial test for my reference: print("m is chosen and the contents are:\n" + arg.f.read())
#parser.add_argument("-t", type= str, help="testing")
#parser.add_argument("-m", type= int, help="test2")