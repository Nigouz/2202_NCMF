#import modules
import cv2
import pytesseract
import csv

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def image_processing(img):
    grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # converting it to binary image
    # thresholding is a segementation techniques in computer vision, allowing us to separate the 
    # foregound from the background of the an image
    # Thresholding is the binarization of an image. 
    # 
    # In general, we seek to convert a grayscale image to a binary image, where the pixels are either 0 or 255.
    # To construct this thresholded image I simply set my threshold value T=225. 
    # That way, all pixels p in the logo where p < T are set to 255, and all pixels p >= T are set to 0
    # 
    # But in the case that you want your objects to appear as black on a white background, 
    # be sure to supply the cv2.THRESH_BINARY flag.
    
    # [1] cv2.threshold returns a tuple of 2 values, in this case we only want the second value which is the img
    thresh_img = cv2.threshold(grey_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # But now that we are using Otsu’s method for automatic thresholding, this value of T becomes interesting 
    # — we do not know what the optimal value of T is ahead of time, 
    # hence why we are using Otsu’s method to compute it for us.
    
    #cv2.imwrite('threshold.png', thresh_img)
    return thresh_img

def get_data(thresh_img):
    # parameters configured for tesseract usage
    oem_psm_config = r'--oem 3 --psm 6' 

    # image_to_data returns result containing box boundaries, confidences, and other information
    # If you print the details, these are the dictionary keys that will contain relevant details:
    # dict_keys(['level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num', 'left', 'top', 'width', 'height', 'conf', 'text'])
    data = pytesseract.image_to_data(thresh_img, output_type=pytesseract.Output.DICT, config=oem_psm_config, lang='chi_sim')
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
    
    filename = input("\nWhat do you want to name your image? ")
    filename = filename + ".png"

    cv2.imwrite(filename, img)        # saving image
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
    with open(filename, 'w', newline="") as file:
       csv.writer(file, delimiter=" ").writerows(text) 
    
if __name__ == "__main__":
    try:
        image_file = input("Which image do you want to extract the text from in your current directory? Please inculde the extension (.png, .jpg)\n")
        img = cv2.imread(image_file)
        
        thresholds_img = image_processing(img)        
        read_data = get_data(thresholds_img)
        accuracy_threshold = 30
        draw_rect(thresholds_img, read_data, accuracy_threshold)
        arranged_text = append_info(read_data)
        save_info(arranged_text)
    except KeyboardInterrupt:
        print("\n\nYou ended the program :) ")
    except cv2.error:
        print("\n\nFile name could not be found or File extension is not accepted... \nPlease run the program again :( ")