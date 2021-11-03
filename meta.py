from PIL import Image
from PIL.ExifTags import TAGS

def metadata_img(filename):
    image = Image.open(filename)
    exifdata = image.getexif()

    if not exifdata:
        print("No metadata found! :(")

    for tag_id in exifdata:
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)

        if isinstance(data, bytes):
            data = data.decode()
        with open('test.txt', 'a') as file1:
            file1.write(f"{tag:25}: {data} \n")

filename1 = input("What is the name of your image? (exclude extension): ")
metadata_img(filename1)
