import glob
import os

import pytesseract
from PIL import Image as PILImage
from wand.image import Image as WandImage


def process(directory_with_pdfs, verbose=True):
    pdfs = glob.glob(os.path.join(directory_with_pdfs, "*.pdf"))



    #
    # for paper in papers:
    #     print("Processing paper: {}...".format(paper.filename))
    #     tokens = [t for t in paper.text.split()]
    #     clean_tokens = [token for token in tokens if token not in stopwords.words("english")]
    #
    #     freq = nltk.FreqDist(clean_tokens)
    #     filename = paper.filename.split(".")[0].split("/")[1] + ".txt"
    #     with open("frequencies/" + filename, "w") as freq_file:
    #         for key, val in sorted(freq.items(), key=lambda x: x[1], reverse=True):
    #             freq_file.write(str(key) + ' : ' + str(val) + "\n")


def get_text_from_pdf(filename, directory="images", verbose=True):
    """
    Use Tesseract OCR to get the text from filename. PDFs are converted pagewise into
    jpegs and saved in directory
    Further Tesseract OCR usage instructions: https://anaconda.org/jiayi_anaconda/pytesseract
    :param filename: pdf to get the text from
    :param directory: Save location for jpeg versions of the pdf. "images" by default
    :param verbose: Enable logging to standard output. False by default
    :return: a list of strings, each string being one page of the pdf
    """

    # Make sure pytesseract knows where tesseract is stored
    pytesseract.pytesseract.tesseract_cmd = '/anaconda3/envs/MemosToNotes3/bin/tesseract'

    with WandImage(filename=filename, resolution=200) as image:
        image.compression_quality = 60

        # Use the filename sans extension as a user-friendly id of that file
        file_id = filename.split(os.sep)[-1].split(".")[0]
        images_directory = os.path.join(directory, file_id)

        # Create the directory if it doesn't exist already
        if not os.path.exists(images_directory):
            os.makedirs(images_directory)

        jpg_path = os.path.join(images_directory, file_id + ".jpg")
        if verbose:
            print("Saving image file: " + jpg_path)
        image.save(filename=jpg_path)

    # now get all the .jpg files, and use tesseract on them
    filenames = sorted(glob.glob(os.path.join(directory, file_id, "*.pdf")))
    pdf_text = []
    for i, filename in enumerate(filenames, 1):
        if verbose:
            print("Processing {} (file {} out of {})... ".format(filename, i, len(filenames)), end="")
        pdf_text.append(pytesseract.image_to_string(PILImage.open(filename)))
        if verbose:
            print("Done")
    return pdf_text


def main():
    print("".join(get_text_from_pdf("pdfs/ocr_1.pdf")))


if __name__ == '__main__':
    main()
