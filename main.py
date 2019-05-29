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


def get_text_from_pdf(pdf_path: str, root: str = "corpus", verbose: bool = True, reuse=True) -> list:
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
                print("Saving image file: " + image_path)
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
                print("Processing '{}' ({} out of {})".format(pdf_path, i, len(pdf_paths)))

            # Write the data to the appropriate text file
            with open(text_file_path, "w+") as text_file:
                text_file.writelines(get_text_from_pdf(pdf_path, verbose=verbose, reuse=reuse))
        else:
            # already-processed files exist, and the user wants to use them
            if verbose:
                print("'{}' Already exists. ({} out of {})".format(pdf_path, i, len(pdf_paths)))


def text_to_json(root, extra_words=None):
    """
    From a given dictionary of pdf_name:text pairs, extract the word:frequency pairs into
    adjacent lists
    :param root: Root file in which to work. Should contain root/txts and root/summaries
    :param extra_words:
    :return: (words, frequencies) tuple
    """
    txt_files = sorted(glob.glob(os.path.join(root, "txts", "*.txt")))
    for txt_file in txt_files:
        with open(txt_file, "r") as txt:
            text = "\n".join(txt.readlines())

        # Preprocessing
        # Remove all duplicates, and make all the words lowercase
        unique_words = list(set([word.lower() for word in text.split()] + extra_words))
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


def json_to_graph(json_path, limit=100):
    """
    Plot and show a bar graph with the frequencies of the words in dictionary
    Case insensitive
    :param json_path:
    :param limit:
    :param unique_words:
    :param frequencies:
    """

    # json_path = "corpus/summaries/2011 June Memo.json"
    with open(json_path, "r") as jsonfile:
        data: dict = json.load(jsonfile)
    unique_words, frequencies = list(data.keys()), list(data.values())

    index = np.arange(len(unique_words[:limit]))
    plt.figure(figsize=(13, 4), dpi=400)
    plt.bar(index, frequencies[:limit])
    plt.xlabel('Word', fontsize=5)
    plt.ylabel('Frequency', fontsize=5)
    plt.xticks(index, unique_words[:limit], fontsize=5, rotation=60)
    plt.title('Frequency of words in CSC Papers')
    plt.tight_layout()
    plt.savefig(json_path.split(".")[0] + ".png")
    # plt.show()


def main():
    # Process the corpus of memos:
    pdfs_to_texts()
    json_to_graph("corpus/summaries/2011 June Memo.json")

    # Process the corpusses of each topic:
    # topic_pdfs = glob.glob("topics/pdfs/*.pdf")
    # for topic_pdf in topic_pdfs:
    #     pass

    # words, frequencies = get_words_and_freqs(process_pdfs("_topics", reuse=True))
    # plot_bar_graph(words, frequencies)

    # print(""./join(get_text_from_pdf("memos/ocr_1.pdf")))


if __name__ == '__main__':
    main()
