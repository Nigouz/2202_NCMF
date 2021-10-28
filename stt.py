import speech_recognition as sr
import os, mimetypes, argparse
from argparse import ArgumentParser
from pydub import AudioSegment
from collections import Counter

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

        #If file is not wav file, perform conversion first before calling text conversion func.
        #As long as audio ext is supported by ffmpeg, the audio file can be converted to wav                                                          
        if ext !='.wav':
            anotherfile = AudioSegment.from_file(arg.f.name)
            result = anotherfile.export("converted.wav", format="wav")
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
    #counter()
    #sus_words()
    options()

def options():
    while True:
        try: 
            option = int(input("0 - None \n1 - Count top no. of words \n2 - Check for sus words\n3 - Do both options\n\n"))
            if option == 0:
                break
            elif option == 1:
                counter()
                break
            elif option == 2:
                sus_words()
                break
            elif option == 3:
                counter()
                sus_words()
                break
            else:
                print("Invalid option\n")
        except ValueError:
            print("Please try again!\n")

        

        
    

#Function to count the most number of common words that appeared in the audio file
def counter():
    while True: 
        try:
            ans = int(input("How many Top common words would like to get? eg: 0, 1, 2, 3 \n"))
            if ans == 0:
                break
            words = []
            with open('text.txt', 'r') as f:
                for line in f:
                    words.extend(line.split())
            
            counts = Counter(words)
            with open('text.txt', 'a') as counted:
                counted.write("\n\nTOP " + str(ans) + " MOST COMMON WORDS:")
                for key, value in counts.most_common(ans):
                    counted.write("\n")
                    counted.write(key)
                    counted.write(": ")
                    counted.write(str(value))
            break
        except ValueError:
            print("Please try again!")

def sus_words():
    words_list = []
    sus_list = []
    with open('sus.txt', 'r') as file2:
        for line in file2:
            sus_list.extend(line.split())

    with open('text.txt', 'r') as file1:
        for line in file1:
            words_list.extend(line.split())
    for i in range(len(words_list)):
        words_list[i] = words_list[i].lower()
    #file = open('text.txt','r')
    with open('text.txt', 'a') as add:
        add.write("\n\n" + "Suspicious words found: \n")
    for i in sus_list:
        if i in words_list: 
            with open('text.txt', 'a') as add:
                add.write(i + "\n")
       

def main():
    arguments= arg_parser()
    file_checker()

if __name__ == "__main__":
    main()


### For my own references ###
#Initial test for my reference: print("m is chosen and the contents are:\n" + arg.f.read())
#parser.add_argument("-t", type= str, help="testing")
#parser.add_argument("-m", type= int, help="test2")
