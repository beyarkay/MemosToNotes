import glob
import os

import numpy as np
import pytesseract
from PIL import Image as PILImage
from matplotlib import pyplot as plt
from wand.image import Image as WandImage


def get_text_from_pdf(pdf: str, directory: str = "images", verbose: bool = True, reuse=True) -> list:
    """
    Use Tesseract OCR to get the text from filename. PDFs are converted pagewise into
    jpegs and saved in directory
    Further Tesseract OCR usage instructions: https://anaconda.org/jiayi_anaconda/pytesseract
    :rtype: list
    :param pdf: pdf to get the text from
    :param directory: Save location for jpeg versions of the pdf. "images" by default
    :param verbose: Enable logging to standard output. False by default
    :return: a list of strings, each string being one page of the pdf
    """

    # Make sure pytesseract knows where tesseract is stored
    pytesseract.pytesseract.tesseract_cmd = '/anaconda3/envs/MemosToNotes3/bin/tesseract'

    # First convert the pdf to an image
    with WandImage(filename=pdf, resolution=200) as image:
        image.compression_quality = 60

        # Use the filename sans extension as a user-friendly id of that file
        file_id = pdf.split(os.sep)[-1].split(".")[0]
        images_directory = os.path.join(directory, file_id)
        jpg_path = os.path.join(images_directory, file_id + ".jpg")

        # Create the directory if it doesn't exist already
        if not os.path.exists(images_directory):
            os.makedirs(images_directory)
        elif not reuse and "n" == input(
                images_directory + " already exists. Do you want to use it's contents? (y/n): "):
            if verbose:
                print("Saving image file: " + jpg_path)
            image.save(filename=jpg_path)

    # now get all the .jpg files, and use tesseract on them
    images = sorted(glob.glob(os.path.join(directory, file_id, "*.jpg")))
    pdf_text = []
    for i, image in enumerate(images, 1):
        if verbose:
            print("Extracting text from {} (file {} out of {})... ".format(image, i, len(images)), end="")
        pdf_text.append(pytesseract.image_to_string(PILImage.open(image)))
        if verbose:
            print("Done")
    return pdf_text


def process_pdfs(directory_with_pdfs, verbose=True, reuse=True):
    """
    Collects all the text from various pdfs into one dictionary, ready for analysis
    :param directory_with_pdfs: path to the directory with the pdfs
    :param verbose: whether or not to log to standard output
    :return: dictionary of text from all the pdfs
    """
    while not os.path.exists(directory_with_pdfs):
        directory_with_pdfs = input(directory_with_pdfs + " doesn't exist. Enter another one: ")
    pdfs = sorted(glob.glob(os.path.join(directory_with_pdfs, "*.pdf")))
    pdf_dict = {"all_text": ""}

    for i, pdf in enumerate(pdfs, 1):
        file_id = pdf.split(os.sep)[-1].split(".")[0]

        # Create the directory if it doesn't exist already
        text_dir_path = os.path.join("text_files", file_id)
        if not os.path.exists(text_dir_path):
            os.makedirs(text_dir_path)
        text_file_path = os.path.join(text_dir_path, file_id + ".txt")

        if not reuse or len(glob.glob1(text_dir_path, "*.txt")) == 0:
            # The user doesn't want to reuse the already-processed files
            if verbose:
                print("Processing '{}' ({} out of {})".format(pdf, i, len(pdfs)))
            pdf_dict[pdf] = get_text_from_pdf(pdf, verbose=verbose)
            # Write the data to the appropriate text file
            with open(text_file_path, "w+") as text_file:
                text_file.writelines(pdf_dict[pdf])
        else:
            # already-processed files exist, and the user wants to use them
            if verbose:
                print("'{}' Already exists. Using existing data. ({} out of {})".format(pdf, i, len(pdfs)))
            with open(text_file_path, "r") as text_file:
                pdf_dict[pdf] = text_file.readlines()

        pdf_dict["all_text"] += "\n".join(pdf_dict[pdf])

    return pdf_dict


def plot_bar_graph(dictionary):
    """
    Plot and show a bar graph with the frequencies of the words in dictionary
    :param dictionary:
    """
    # stop_words: list = stopwords.words("english")
    all_text: list = dictionary["all_text"].split()
    unique_words = list(set(all_text))
    frequencies = [all_text.count(word) for word in unique_words]

    together = sorted(zip(unique_words, frequencies), key=lambda x: x[1], reverse=True)

    unique_words = [item[0] for item in together]
    frequencies = [item[1] for item in together]

    index = np.arange(len(unique_words[:30]))
    plt.bar(index, frequencies[:30])
    plt.xlabel('Word', fontsize=5)
    plt.ylabel('Frequency', fontsize=5)
    plt.xticks(index, unique_words[:30], fontsize=5, rotation=30)
    plt.title('Frequency of words in CSC Papers')
    plt.show()


def main():
    plot_bar_graph(process_pdfs("pdfs"))

    print("".join(get_text_from_pdf("pdfs/ocr_1.pdf")))


if __name__ == '__main__':
    main()
