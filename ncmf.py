# For STT
import speech_recognition as sr
import os, mimetypes, shutil
from argparse import ArgumentParser
from pydub import AudioSegment
from pydub.utils import mediainfo, make_chunks
from collections import Counter
# For ITT
import cv2
import pytesseract
import csv
from PIL import Image
from PIL.ExifTags import TAGS

colors = {'HEADER': "\033[95m",
          'YELLOW': "\033[93m",
          'LIGHTBLUE': "\033[96m",
          'END': "\033[0m"}

# Amend file path according to where you have installed tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# original cwd where script is ran
global ogcwd
ogcwd = os.getcwd()


def arg_parser():
    # Create parser
    parser = ArgumentParser(description="For more information regarding o options, please run 'ncmf.py o -h' ")
    parser.add_argument('-r', type=str, help="Specify audio file for conversion")
    parser.add_argument('-i', type=str, help="Specify image file for OCR")
    parser.add_argument('-s', type=str, default="default_sus_list.txt",help="Specify your own suspicious word list text file")
    parser.add_argument('-m', type=str, help="Specify your foldername containing audio files")
    parser.add_argument('-n', default=3, type=int, help="Specify number of top words you wish to list")

    # Create Subparser for Word Count + Sus Word Function
    options = parser.add_subparsers(dest="opt", help='help for options subcommands')
    # add the arguments to subparser to run the option check for word counter & sus words
    parser_options = options.add_parser("o", help="To select options for Word Tracker & Suspicious Words function on text files")
    parser_options.add_argument('-a', type=str, help="To count the top 3 number of words seen & check for suspicious words in file")
    parser_options.add_argument('-b', type=str, help="To count the top 3 number of words seen in file")
    parser_options.add_argument('-c', type=str, help="To check for suspicious words mentioned")

    return parser.parse_args()


def file_checker():
    arg = arg_parser()  # So that we can use the variables from arg_parser function
    # ensure that this argument input is a txt file before program continues running

    if arg.s:
        path = os.path.realpath(arg.s)  # to get file path
        ext = os.path.splitext(path)[1]  # to obtain file name and file extension
        ext.lower()
        if ext != '.txt':
            print("Error! Please only input .txt files when -s is used to specify text file you wish to search suspicious words against.")
            return

    if arg.m:
        nonfile = 0  # to see if there are any non files in folder
        cwd = os.getcwd()
        # folder user inputted
        searchfolder = os.scandir(arg.m)
        foldername = input("What do you want to name new folder for translation result (folder will be created in current directory): ")
        folder = foldername
        # Ensure folder don't exist before creating new folder to store converted audio files
        try:
            os.mkdir(folder)
        except OSError as ee:
            print("Folder exists, please try again")
            return

        for file in searchfolder:
            # to determine if item is a file
            if os.path.isfile(file):
                # If item is file, try to convert it into .wav for transcribing
                path = os.path.realpath(file)  # to get file path
                ext = os.path.splitext(path)[1]

                obtainduration = AudioSegment.from_file(path)
                fileduration = obtainduration.duration_seconds

                ext.lower()
                if ext != '.wav':
                    try:
                        # print(path)
                        anotherfile = AudioSegment.from_file(path)
                        anotherfile.export("%s/%s_converted.wav" % (folder, file.name), format="wav")

                    except Exception as e:
                        # print (e)
                        print("Error! %s is not a valid audio file. Kindly ensure that only valid audio files are in this folder." % file.name)
                        return

                if ext == '.wav':
                    # Copy the file into the new folder
                    shutil.copy(file.name, "%s/%s" % (folder, file.name))
            else:
                nonfile += 1

        if nonfile >= 1:
            print("Kindly ensure that only valid audio files are in this folder. No sub folders should be present.")
        else:
            convertedfolder = os.scandir(folder)
            for audiofile in convertedfolder:
                updatepath = "%s/%s" % (cwd, folder)
                # change current dir path to the created folder's path so that we can append all the converted things over there
                os.chdir(updatepath)
                get_metadata(audiofile.name)
                if float(fileduration) > 60.0:  # if the duration is more than 60sec, split to chunks
                    largefile_minmiser(audiofile.name)

                else:
                    converter(audiofile.name)

    # if user is parsing an image file for OCR
    if arg.i:
        try:
            # Verify if file can be read by cv2, if it does, run the OCR
            img = cv2.imread(arg.i)
            metadata_img(arg.i)
            thresholds_img = image_processing(img)
            read_data = get_data(thresholds_img)
            accuracy_threshold = 30
            draw_rect(thresholds_img, read_data, accuracy_threshold)
            arranged_text = append_info(read_data)
            filename = save_info(arranged_text)
            sus_words(filename)
            counter(filename, arg.n)


        except KeyboardInterrupt:
            print("\n\nYou ended the program :) ")
        except cv2.error:
            print("\n\nFile name could not be found or File extension is not accepted... \nPlease run the program again :( ")

    # if user is parsing text file for the counter function
    if arg.opt:
        # check file's extension
        if arg.a:
            path = os.path.realpath(arg.a)  # to get file path
            ext = os.path.splitext(path)[1]
            ext.lower()
            if ext == '.txt':
                counter(arg.a, arg.n)
                sus_words(arg.a)

        elif arg.b:
            path = os.path.realpath(arg.b)  # to get file path
            ext = os.path.splitext(path)[1]
            ext.lower()
            if ext == '.txt':
                counter(arg.b, arg.n)

        elif arg.c:
            path = os.path.realpath(arg.c)  # to get file path
            ext = os.path.splitext(path)[1]
            ext.lower()
            if ext == '.txt':
                sus_words(arg.c)

    # if user is parsing an audio file for conversion
    if arg.r:
        path = os.path.realpath(arg.r)  # to get file path
        ext = os.path.splitext(path)[1]
        ext.lower()

        obtainduration = AudioSegment.from_file(path)
        fileduration = obtainduration.duration_seconds

        # If file is not wav file and txt file, perform conversion first
        # As long as audio ext is supported by ffmpeg, the audio file can be converted to wav
        if ext != '.wav' and ext != '.txt' and ext != "":
            try:
                anotherfile = AudioSegment.from_file(arg.r)
                convertedFile = anotherfile.export("%s_converted.wav" % arg.r, format="wav")
                get_metadata(arg.r)
                # print(convertedFile)
                if float(fileduration) > 60.0:  # if the duration is more than 60sec, split to chunks
                    largefile_minmiser(convertedFile.name)

                else:
                    # Call transcription function
                    print("converting file...")
                    converter(convertedFile)
            except Exception as e:
                print(e)
                print("Error! Inputted file is not a valid audio file.")
                return

        # Speech Recognition only runs with .wav files, so if its already .wav, no conversion has to be done, we can begin the speech recognition
        elif ext == '.wav':
            get_metadata(arg.r)

            if float(fileduration) > 60.0:  # if the duration is more than 60sec, split to chunks
                largefile_minmiser(arg.r)

            else:
                converter(arg.r)


# Function that does the conversion with Google API (Limitation: Can only convert up to 60 minutes of audio per day)#Can test with Google Cloud API
def converter(audiofile):
    arg = arg_parser()
    # Call speech recognition lib
    r = sr.Recognizer()
    with sr.AudioFile(audiofile) as src:
        # energy threshold level indicates at which audio level is the audio considered speech
        # Since we have to take into consideration for background noise so I set it to 400
        # Value below are considered silence. Default value is 300
        r.energy_threshold = 400
        # ambient noise duration means how long will SR take to listen for background noise before adjusting energy treshold
        r.adjust_for_ambient_noise(src, duration=0.5)
        # listen for data
        audio = r.record(src)
        text = r.recognize_google(audio, language='en')
        try:
            if arg.r:
                filename = "%s.txt" % arg.r

            if arg.m:
                filename = "%s.txt" % audiofile
                # Open a new file to write the transcript (name it the same as audio file but with .txt ext)
            with open(filename, 'a', encoding="utf-8") as textfile:

                for x in text:
                    textfile.write(x)

            if arg.r:
                print("%s has been transcribed and saved into %s in current directory." % (arg.r, filename))

            if arg.m:
                print("%s has been transcribed and saved into %s in current directory." % (audiofile, filename))

            # Run the sub function (counter + suspicious words) by default for audio files
            counter(filename, arg.n)
            sus_words(filename)
        except KeyboardInterrupt:
            print("\n\nYou ended the program :) ")
        except sr.UnknownValueError as e:
            print("Error! Audio might be too fast or have too much background noise for conversion to be performed.")


def converter_chunks():  # translate each chunk
    r = sr.Recognizer()
    try:
        print("\n++++ Processing your files now ++++ Please wait :)")
        for i in listofchunks:  # previously we stored all the chunk filename in this list
            with sr.AudioFile(i) as src:
                r.energy_threshold = 400
                r.adjust_for_ambient_noise(src, duration=0.5)
                # listen for data
                audio = r.record(src)
                # convert speech to text
                text = r.recognize_google(audio, language='en')
                # i added the audio, language='en-IN',show_all=True, show all will show all alternatives
                with open(i + '_translated.txt', 'w') as textfile:
                    for x in text:
                        textfile.write(x)
        concate_chunks()
    except KeyboardInterrupt:
        print("\n\nYou ended the program :) ")
    except sr.UnknownValueError as e:
        print("Audio might be too fast or have too much background noise for conversion to be performed")


def concate_chunks():
    arg = arg_parser()
    filename = filename_m + ".txt"  # whatever file name pass to largefileminimiser will be pass here
    print("\nTranslating now . . . ")
    with open(filename, "a", encoding="utf-8") as combineFile:
        # combineFile.write("Transcripted Text:\n")
        for x in listofchunks_To_translated:  # list of chunks is all the chunk filename created
            with open(x) as infile:
                contents = infile.read()
                # combineFile.write("Chunk: "+ x)
                # combineFile.write("\n")
                combineFile.write(contents.lower())
    if arg.r:
        print("\n%s has been transcribed successfully, %s is at:" % (arg.r, filename), os.getcwd())
        counter(filename, 3)
        sus_words(filename)
    elif arg.m:
        print("\n%s has been transcribed successfully, %s is at:" % (filename_m, filename), os.getcwd())
        counter(filename, 3)
        sus_words(filename)


def largefile_minmiser(audiofile):
    # Split any file longer than 1 minute
    myaudio = AudioSegment.from_file(audiofile)
    chunk_length_ms = 60000  # pydub calculates in millisec (i have changed it to one minute)
    chunks = make_chunks(myaudio, chunk_length_ms)  # Make chunks of one minute, basically just divide
    global filename_m  # this variable will be used by concate_chunks

    # print("Explicit argument provided for this function:",audiofile)
    # print("parsed audio:",audiofile.name)
    filename_m = audiofile
    # print("trying to replace audio file: ", audiofile.name)
    filename_forchunk = filename_m.replace('.wav', '')
    # Export all of the individual chunks as wav files
    print('\n')
    print("This file is longer than 1 minute and will be split into chunks for analysing")

    global listofchunks, listofchunks_To_translated
    listofchunks = []  # first, create a list to store these chunks so we can do a loop later
    listofchunks_To_translated = []

    # filename = input("What do you want to name your chunks? (exclude extension): ")
    for i, chunk in enumerate(chunks):
        chunk_name = filename_forchunk + "_chunk{0}.wav".format(
            i)  # filenameONLY is the global variable created in file_checker()
        print("splitting into >>", chunk_name)
        chunk.export(chunk_name, format="wav")
        listofchunks.append(chunk_name)
        listofchunks_To_translated.append(chunk_name + "_translated.txt")
    converter_chunks()
    # print(filename) = "bravestfish" without extension
    # print(chunk_name) = "bravestfish_chunk1.wav"


# Function to count the most number of common words that appeared in the audio file
def counter(filename, number):
    while True:
        try:
            if number == 0:
                break
            words = []
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    words.extend(line.split())

            counts = Counter(words)
            with open(filename, 'a', encoding='utf-8') as counted:
                counted.write("\n\nTOP " + str(number) + " MOST COMMON WORDS:")
                for key, value in counts.most_common(number):
                    counted.write("\n")
                    counted.write(key)
                    counted.write(": ")
                    counted.write(str(value))
            break
        except ValueError:
            print("Please try again!")


# Function to search for suspicious words to flag out
def sus_words(filename):
    arg = arg_parser()  # To access arg.s variable
    words_list = []
    sus_list = []

    if arg.m:
        with open("%s/%s" % (ogcwd, arg.s), 'r') as file2:
            for line in file2:
                sus_list.extend(line.split())
                sus_list = [i.lower() for i in sus_list]

    if arg.r:
        with open(arg.s, 'r') as file2:
            for line in file2:
                sus_list.extend(line.split())
                sus_list = [i.lower() for i in sus_list]
    if arg.i:
        with open(arg.s, 'r') as file2:
            for line in file2:
                sus_list.extend(line.split())
                sus_list = [i.lower() for i in sus_list]

    if arg.opt:
        with open(arg.s, 'r') as file2:
            for line in file2:
                sus_list.extend(line.split())
                sus_list = [i.lower() for i in sus_list]

    # File 1 is the transcripted file
    with open(filename, 'r', encoding='utf-8') as file1:
        for line in file1:
            words_list.extend(line.split())
    for i in range(len(words_list)):
        words_list[i] = words_list[i].lower()

    with open(filename, 'a', encoding='utf-8') as add:
        add.write("\n\n" + "Suspicious words found: \n")
    for i in sus_list:
        if i in words_list:
            with open(filename, 'a') as add:
                add.write(i + "\n")

    print("\nThank you for using NCMF's Audio/Image Analyser")


# Function to retrieve metadata information
def get_metadata(file):
    # pydub lib - printing information from Metatags
    metadata = mediainfo(file)
    path = os.path.realpath(file)
    # retrieve file duration to determine whether file minimizing has to be done
    # global fileduration  # Set to global variable so that we can access it in the filechecker function
    # fileduration = metadata['duration']
    # Write metadata information into a text file & specify utf-8 encoding to prevent anyawy encoding issues || utf-8 selected since it can handle all the chars
    # https://stackoverflow.com/questions/16346914/python-3-2-unicodeencodeerror-charmap-codec-cant-encode-character-u2013-i
    with open("%s_metadata.txt" % (path), 'w', encoding='utf-8') as textfile:
        textfile.write("To Note:\nProbe score refers to the likelihood of the audio file being converted from its original format. The higher the score, the less likely an audio file has been converted.\nDo note that manually changing the file extensions will not change the probe score. Audio file needs to be properly converted for probe score to change.\n")
        for keys, values in metadata.items():
            # pydub lib - To retrieve relevant information such as: file name, file type, file size, duration (in seconds and in ts format), probe score, media time base rate
            if keys == "filename":
                textfile.write("\nFile Name: ")
                textfile.write(values)

            if keys == "format_name":
                textfile.write("\nFile Format: ")
                textfile.write(values)

            if keys == "format_long_name":
                textfile.write("\nFile Format (Long version): ")
                textfile.write(values)

            if keys == "size":
                textfile.write("\nFile size (in bytes): ")
                textfile.write(values)

            if keys == "duration":
                textfile.write("\nAudio Duration (in seconds): ")
                textfile.write(values)

            if keys == "probe_score":
                textfile.write("\nProbe score: ")
                textfile.write(values)

            # On what media time base is
            # https://www.conservation-wiki.com/wiki/Time-Based_Media & https://video.stackexchange.com/questions/27546/difference-between-duration-ts-and-duration-in-ffprobe-output
            # https://stackoverflow.com/questions/43333542/what-is-video-timescale-timebase-or-timestamp-in-ffmpeg/43337235#43337235
            if keys == "time_base":
                textfile.write("\nMedia Time Base Rate: ")
                textfile.write(values)

            if keys == "duration_ts":
                textfile.write("\nAudio Duration (in media's time base): ")
                textfile.write(values)

            # pydub lib - To retrieve metadata information from TAG value
            if keys == "TAG":
                # iterate the TAG dictionary
                for key in values:
                    textfile.write("\n")
                    textfile.write(key)
                    textfile.write(": ")
                    textfile.write((values[key]))

    path = os.path.realpath(file)  # to get file path for new file
    print("Metadata has been saved in %s.txt in %s." % (file, path))


def image_processing(img):
    # convert the image to grayscale to allow thresholding
    grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # conduct threshold with 2 types of thresholding, in most cases cv2.THRESH_OTSU will be use
    # cv2.threshold returns a tuple of 2 values, in this case we only want the second value which is the img therefore use [1]
    thresh_img = cv2.threshold(grey_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # return threshold image to get the data
    return thresh_img


def get_data(thresh_img):
    # parameters configured for tesseract usage
    oem_psm_config = r'--oem 3 --psm 6'

    # image_to_data returns result containing box boundaries, confidences, and other information
    # If you print the details, these are the dictionary keys that will contain relevant details:
    # dict_keys(['level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num', 'left', 'top', 'width', 'height', 'conf', 'text'])
    data = pytesseract.image_to_data(thresh_img, output_type=pytesseract.Output.DICT, config=oem_psm_config, lang='eng')
    # return data to get draw the rectangle box surrounding the text and to obtain the relevant text to input into a text file
    return data


def draw_rect(img, data, thresh_point):
    # number of text box(rectangles) based on 'text' key-value
    num_rect = len(data['text'])

    for i in range(num_rect):
        # consider only those images whose confidence score is greater than 30
        if float(data['conf'][i]) > thresh_point:
            # take in the values of the sepecific key-value pair
            (x, y, w, h) = (data['left'][i], data['top'][i],
                            data['width'][i], data['height'][i])
            # draw the rectangle with the given details, color, thickness of the line
            img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    filename = input("\nWhat do you want to name your Captured-text image? ")
    filename = filename + ".png"

    cv2.imwrite(filename, img)  # saving image
    print("Captured-text image has been saved to your local folder")


def append_info(data):
    read_text = []
    total_words = []
    next_word = ''
    for word in data['text']:
        if word != '':
            total_words.append(word)
            next_word = word

        # the end
        # there's a last word and no more words | last value in the text
        if (next_word != '' and word == '') or (word == data['text'][-1]):
            # put it in the parse_text list
            read_text.append(total_words)
            total_words = []

    return read_text


def save_info(text):
    filename = input("\nWhat do you want to name your text file? ")
    filename = filename + ".txt"
    with open(filename, 'w', newline="", encoding="utf-8") as file:
        csv.writer(file, delimiter=" ").writerows(text)
    return filename


def metadata_img(filename):
    image = Image.open(filename)
    exifdata = image.getexif()

    if not exifdata:
        print("No metadata found! :(")
        return

    for tag_id in exifdata:
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)

        if isinstance(data, bytes):
            data = data.decode()
        img_metadata = filename + "_metadata.txt"
        with open(img_metadata, 'a') as file1:
            file1.write(f"{tag:25}: {data} \n")
    print("Image metadata has been saved to your local folder")


def logo():
    print("--------------------------------------")
    print(" _______   ______   __      __   _____")
    print("|    |  | |   ___| |  \    /  | |   __|")
    print("|    |  | |  |     |   \  /   | |  |_")
    print("|  |    | |  |___  |    \/    | |   _|")
    print("|__|____| |______| |__|\__/|__| |__|")
    print()
    print("--------------------------------------")
    print("[!] -h for Help")
    print("[!] o -h for Options Help")
    print("[!] Examples:")
    print("# python ncmf.py -i sample_image.png")
    print("# python ncmf.py -r music.mp3")
    print("# python ncmf.py -r music.ogg -i sample_image.jpg")
    print("# python ncmf.py -i sample_image.jpg -n 5")
    print("# python ncmf.py -m foldername")
    print("--------------------------------------")
    print("*Note: No metadata will be returned for a non jpg file\n")
    print("*Warning: For analysing text file, results will be append onto your text file which will affect data integrity \n")
    print("*Warning: Please take the necessarily precautions when using text function\n")

def main():
    logo()
    arguments = arg_parser()
    file_checker()


if __name__ == "__main__":
    main()
