import glob
import json
import os

import numpy as np
import pytesseract
from PIL import Image as PILImage
from matplotlib import pyplot as plt
from wand.color import Color
from wand.image import Image as WandImage


def get_filename(pdf_path):
    return pdf_path.split(os.sep)[-1].split(".")[0]


def get_text_from_pdf(pdf_path: str, root: str, verbose: bool = True, reuse=True) -> list:
    """
    Use Tesseract OCR to get the text from filename. PDFs are converted pagewise into
    jpegs and saved in directory
    Further Tesseract OCR usage instructions: https://anaconda.org/jiayi_anaconda/pytesseract
    :param root:
    :param reuse:
    :rtype: list
    :param pdf_path: pdf to get the text from
    :param directory: Save location for jpeg versions of the pdf. "images" by default
    :param verbose: Enable logging to standard output. False by default
    :return: a list of strings, each string being one page of the pdf
    """

    # Make sure pytesseract knows where tesseract is stored
    pytesseract.pytesseract.tesseract_cmd = '/anaconda3/envs/MemosToNotes3/bin/tesseract'

    # First convert the pdf to an image
    with WandImage(filename=pdf_path, resolution=200) as image:
        image.compression_quality = 60

        # Enforce a white background, otherwise some powerpoints just become entirely black images
        image.background_color = Color("white")
        image.alpha_channel = 'remove'

        # Each pdf has to be split into multiple .pngs, so each pdf gets a directory in root/pngs/
        images_directory = os.path.join(root, "pngs", get_filename(pdf_path))

        os.makedirs(images_directory, exist_ok=True)
        if not reuse or len(os.listdir(images_directory)) == 0:
            # Save each set of pngs in their own directory: root/pngs/__filename__/1.png, 2.pngs, etc
            image_path = os.path.join(images_directory, get_filename(pdf_path) + ".png")
            if verbose:
                print("Saving as image file: " + image_path)
            image.save(filename=image_path)

    # now get all the .png files, and use tesseract on them
    images = sorted(glob.glob(os.path.join(images_directory, "*.png")))
    pdf_text = []
    for i, image in enumerate(images, 1):
        if verbose:
            print("\tExtracting text from {} (file {} out of {})... ".format(image, i, len(images)), end="")
        pdf_text.append(pytesseract.image_to_string(PILImage.open(image)))
        if verbose:
            print("Done")
    return pdf_text


def pdfs_to_texts(root, verbose=True, reuse=True):
    """
    Collects all the text from various memos into one dictionary, ready for analysis
    :param root:
    :param reuse:
    :param verbose: whether or not to log to standard output
    :return: dictionary of text from all the memos
    """
    directory_with_pdfs = os.path.join(root, "pdfs")
    pdf_paths = sorted(glob.glob(os.path.join(directory_with_pdfs, "*.pdf")))

    for i, pdf_path in enumerate(pdf_paths, 1):
        file_id = get_filename(pdf_path)
        text_file_path = os.path.join(root, "txts", file_id + ".txt")

        if not reuse or not os.path.exists(text_file_path):
            # The user doesn't want to reuse the already-processed files, or those files don't exist
            if verbose:
                print("Opening '{}' ({} out of {})".format(pdf_path, i, len(pdf_paths)))

            # Write the data to the appropriate text file
            with open(text_file_path, "w+") as text_file:
                text_file.writelines(get_text_from_pdf(pdf_path, root=root, verbose=verbose, reuse=reuse))
        else:
            # already-processed files exist, and the user wants to use them
            if verbose:
                print("'{}' Already exists. ({} out of {})".format(pdf_path, i, len(pdf_paths)))


def texts_to_jsons(root, stopwords_file="stopwords.txt"):
    """
    From a given dictionary of pdf_name:text pairs, extract the word:frequency pairs into
    adjacent lists
    :param stopwords_file:
    :param root: Root file in which to work. Should contain root/txts and root/summaries
    :param extra_words:
    :return: (words, frequencies) tuple
    """
    txt_files = sorted(glob.glob(os.path.join(root, "txts", "*.txt")))
    with open(stopwords_file, "r") as stopwords_txt:
        stopwords = set([word.strip() for word in stopwords_txt.readlines()])

    for txt_file in txt_files:
        with open(txt_file, "r") as txt:
            text = "\n".join(txt.readlines())

        # Remove all duplicates, and make all the words lowercase
        unique_words = set([word.lower().strip() for word in text.split()])
        # remove all useless stopwords from the data
        unique_words = list(unique_words - stopwords)

        # Get the frequency of each word
        frequencies = [text.count(word) for word in unique_words]

        # sort the words by their frequency, descending
        sorted_words = sorted(zip(unique_words, frequencies), key=lambda x: x[1], reverse=True)
        clean_words = [item[0] for item in sorted_words]
        frequencies = [item[1] for item in sorted_words]

        # write as json file
        json_path = os.path.join(root, "summaries", get_filename(txt_file) + ".json")
        json_dict = {word: freq for word, freq in zip(clean_words, frequencies)}
        with open(json_path, "w+") as json_file:
            json.dump(json_dict, json_file, indent=2)


def json_to_graph(json_path, num_words=50):
    """
    Plot and show a bar graph with the frequencies of the words in dictionary
    Case insensitive
    :param json_path:
    :param num_words:
    :param unique_words:
    :param frequencies:
    """

    with open(json_path, "r") as jsonfile:
        data: dict = json.load(jsonfile)
    unique_words, frequencies = list(data.keys()), list(data.values())

    index = np.arange(len(unique_words[:num_words]))

    size_ratio = 0.1
    height = 2 * size_ratio * num_words
    width = 1 * size_ratio * num_words
    plt.figure(figsize=(width, height), dpi=400)
    plt.barh(index, frequencies[:num_words])
    plt.ylabel('Word', fontsize=10)
    plt.xlabel('Frequency', fontsize=10)
    plt.yticks(index, unique_words[:num_words], fontsize=7)
    plt.gca().invert_yaxis()
    plt.title('Frequency of words in ' + get_filename(json_path))
    plt.tight_layout()
    plt.savefig(json_path.split(".")[0] + ".png")
    # plt.show()


def update_token_files():
    paths = glob.glob(os.path.join("topics", "pdfs", "*.pdf"))
    for path in paths:
        token_path = os.path.join("topics", "tokens", get_filename(path) + ".txt")
        with open(token_path, "w+") as _:
            pass


def main():
    # Process the corpus of memos:
    pdfs_to_texts("corpus")
    print("texts to jsons")
    texts_to_jsons("corpus")
    print("jsons to graphs")
    json_paths = glob.glob("corpus/summaries/*.json")
    for json_path in json_paths:
        json_to_graph(json_path)


if __name__ == '__main__':
    main()
