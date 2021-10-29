#import modules
import cv2
import pytesseract
import csv
#from pytesseract import image_to_string

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def pre_processing(image):
    """
    This function take one argument as
    input. this function will convert
    input image to binary image
    :param image: image
    :return: thresholded image
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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
    threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    
    #
    # But now that we are using Otsu’s method for automatic thresholding, this value of T becomes interesting 
    # — we do not know what the optimal value of T is ahead of time, 
    # hence why we are using Otsu’s method to compute it for us.

    # saving image to view threshold image
    cv2.imwrite('thresholded.png', threshold_img)

    cv2.imshow('threshold image', threshold_img)
    # Maintain output window until
    # user presses a key
    cv2.waitKey(0)
    # Destroying present windows on screen
    cv2.destroyAllWindows()

    return threshold_img


def parse_text(threshold_img):
    """
    This function take one argument as
    input. this function will feed input
    image to tesseract to predict text.
    :param threshold_img: image
    return: meta-data dictionary
    """
    # configuring parameters for tesseract
    tesseract_config = r'--oem 3 --psm 6'
    # now feeding image to tesseract
    # image_to_data Returns result containing box boundaries, confidences, and other information

    # So we’re going to search for the word “dog” in the text document, 
    # we want the output data to be structured and not a raw string, 
    # that’s why I passed output_type to be a dictionary, 
    # so we can easily get each word’s data (you can print data dictionary to see how the output is organized).

    # If you print the details, these are the dictionary keys that will contain relevant details:
    # dict_keys(['level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num', 'left', 'top', 'width', 'height', 'conf', 'text'])
    details = pytesseract.image_to_data(threshold_img, output_type=pytesseract.Output.DICT,
                                        config=tesseract_config, lang='eng')
    print(details)
    return details


def draw_boxes(image, details, threshold_point):
    """
    This function takes three argument as
    input. it draw boxes on text area detected
    by Tesseract. it also writes resulted image to
    your local disk so that you can view it.
    :param image: image
    :param details: dictionary
    :param threshold_point: integer
    :return: None
    """
    # number of text box based on 'text' key-value
    total_boxes = len(details['text'])

    for sequence_number in range(total_boxes):
        # consider only those images whose confidence score is greater than 30
        if float(details['conf'][sequence_number]) > threshold_point:
            # take in the values of the sepecific key-value pair
            (x, y, w, h) = (details['left'][sequence_number], details['top'][sequence_number],
                            details['width'][sequence_number], details['height'][sequence_number])
            # draw the rectangle with the given details, color, thickness of the line 
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # saving image to local
    cv2.imwrite('captured_text_area.png', image)
    # display image
    cv2.imshow('captured text', image)
    # Maintain output window until user presses a key
    cv2.waitKey(0)
    # Destroying present windows on screen
    cv2.destroyAllWindows()


def format_text(details):
    """
    This function take one argument as
    input.This function will arrange
    resulted text into proper format.
    :param details: dictionary
    :return: list
    """
    parse_text = []
    word_list = []
    last_word = ''
    for word in details['text']:
        if word != '':
            word_list.append(word)
            last_word = word
        
        # the end 
        # there's a last word and no more words | last value in the text 
        if (last_word != '' and word == '') or (word == details['text'][-1]):

            # put it in the parse_text list 
            parse_text.append(word_list)
            # empty the word list 
            word_list = []

    return parse_text


def write_text(formatted_text):
    """
    This function take one argument.
    it will write arranged text into
    a file.
    :param formatted_text: list
    :return: None
    """
    with open('resulted_text.txt', 'w', newline="") as file:
        csv.writer(file, delimiter=" ").writerows(formatted_text)


if __name__ == "__main__":
    # reading image from local
    image = cv2.imread('sample_image.png')
    # calling pre_processing function to perform pre-processing on input image.
    thresholds_image = pre_processing(image)
    # calling parse_text function to get text from image by Tesseract.
    parsed_data = parse_text(thresholds_image)
    # defining threshold for draw box
    accuracy_threshold = 30
    # calling draw_boxes function which will draw dox around text area.
    draw_boxes(thresholds_image, parsed_data, accuracy_threshold)
    # calling format_text function which will format text according to input image
    arranged_text = format_text(parsed_data)
    # calling write_text function which will write arranged text into file
    write_text(arranged_text)