import glob
import os

import numpy as np
import pytesseract
from PIL import Image as PILImage
from matplotlib import pyplot as plt
from nltk.corpus import stopwords
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


def process_pdfs(root, verbose=True, reuse=True):
    """
    Collects all the text from various memos into one dictionary, ready for analysis
    :param root:
    :param reuse:
    :param verbose: whether or not to log to standard output
    :return: dictionary of text from all the memos
    """
    directory_with_pdfs = os.path.join(root, "pdfs")
    pdf_paths = sorted(glob.glob(os.path.join(directory_with_pdfs, "*.pdf")))
    pdf_dict = {"all_text": ""}

    for i, pdf_path in enumerate(pdf_paths, 1):
        file_id = get_filename(pdf_path)
        text_file_path = os.path.join(root, "txts", file_id + ".txt")

        if not reuse or not os.path.exists(text_file_path):
            # The user doesn't want to reuse the already-processed files, or those files don't exist
            if verbose:
                print("Processing '{}' ({} out of {})".format(pdf_path, i, len(pdf_paths)))
            pdf_dict[pdf_path] = get_text_from_pdf(pdf_path, verbose=verbose, reuse=reuse)

            # Write the data to the appropriate text file
            with open(text_file_path, "w+") as text_file:
                text_file.writelines(pdf_dict[pdf_path])
        else:
            # already-processed files exist, and the user wants to use them
            if verbose:
                print("'{}' Already exists. Using existing data. ({} out of {})".format(pdf_path, i, len(pdf_paths)))
            with open(text_file_path, "r") as text_file:
                pdf_dict[pdf_path] = text_file.readlines()

        pdf_dict["all_text"] += "\n".join(pdf_dict[pdf_path])

    return pdf_dict


def get_words_and_freqs(dictionary, use_tokens_file=True):
    """
    From a given dictionary of pdf_name:text pairs, extract the word:frequency pairs into
    adjacent lists
    :param dictionary:
    :param use_tokens_file: WIP
    :return: (words, frequencies) tuple
    """
    if use_tokens_file:
        # Only get results of the tokens in tokens.txt
        with open("tokens.txt", "r") as tokens_file:
            tokens = [token.strip() for token in tokens_file.readlines()]

        text = dictionary["all_text"]
        frequencies = [text.count(word) for word in tokens]
    else:
        # Get frequencies of every single word
        all_words: list = dictionary["all_text"].split()
        unique_words = list(set([word.lower() for word in all_words]))
        clean_words = []
        for word in unique_words:
            clean_word = word.replace(",", ", ")
            if clean_word not in stopwords.words("english"):
                clean_words.append(clean_word)
        frequencies = [all_words.count(word) for word in clean_words]

    together = sorted(zip(tokens, frequencies), key=lambda x: x[1], reverse=True)

    clean_words = [item[0] for item in together]
    frequencies = [item[1] for item in together]

    with open("frequencies.txt", "w+") as file:
        for word, freq in zip(clean_words, frequencies):
            print("{0:<30}:{1}".format(word, freq), file=file)
    return clean_words, frequencies


def plot_bar_graph(unique_words, frequencies):
    """
    Plot and show a bar graph with the frequencies of the words in dictionary
    Case insensitive
    :param unique_words:
    :param frequencies:
    """

    index = np.arange(len(unique_words[:70]))
    plt.figure(figsize=(13, 4), dpi=400)
    plt.bar(index, frequencies[:70])
    plt.xlabel('Word', fontsize=5)
    plt.ylabel('Frequency', fontsize=5)
    plt.xticks(index, unique_words[:70], fontsize=5, rotation=60)
    plt.title('Frequency of words in CSC Papers')

    plt.savefig("Figure1.png")
    plt.show()


def main():
    # Process the corpus of memos:
    corpus_dictionary = process_pdfs("corpus")

    # words, frequencies = get_words_and_freqs(process_pdfs("corpus", reuse=True))

    # Process the corpusses of each topic:
    topic_pdfs = glob.glob("topics/pdfs/*.pdf")
    for topic_pdf in topic_pdfs:
        pass

    # words, frequencies = get_words_and_freqs(process_pdfs("_topics", reuse=True))
    # plot_bar_graph(words, frequencies)

    # print(""./join(get_text_from_pdf("memos/ocr_1.pdf")))


if __name__ == '__main__':
    main()
