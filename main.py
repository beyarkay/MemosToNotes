import glob
import json
import math
import os

import numpy as np
import pytesseract
import seaborn as sns
from PIL import Image as PILImage
from matplotlib import pyplot as plt
from wand.color import Color
from wand.image import Image as WandImage


def get_filename(file_path: str) -> str:
    """
    Utility method to just get the filename from a path, excluding the extension and parent directories
    :param file_path:
    :return:
    """
    return file_path.split(os.sep)[-1].split(".")[0]


def get_text_from_pdf(root: str, pdf_path: str, verbose: bool = True, reuse=True) -> list:
    """
    Use Tesseract OCR to get the text from filename. PDFs are converted pagewise into
    jpegs and saved in savepath
    Further Tesseract OCR usage instructions: https://anaconda.org/jiayi_anaconda/pytesseract
    :param root:
    :param reuse:
    :param pdf_path: pdf to get the text from
    :param verbose: Enable logging to standard output. True by default
    :return: a list of strings, each string being one page of the pdf
    """

    # Make sure pytesseract knows where tesseract is stored
    # CHANGE THIS LINE to be the absolute path to the tesseract unix executable file
    pytesseract.pytesseract.tesseract_cmd = '/anaconda3/envs/MemosToNotes3/bin/tesseract'

    # First convert the pdf to an image
    with WandImage(filename=pdf_path, resolution=200) as image:
        image.compression_quality = 60

        # Enforce a white background, otherwise some powerpoints just become entirely black images
        image.background_color = Color("white")
        image.alpha_channel = 'remove'

        # Each pdf has to be split into multiple .pngs, so each pdf gets a directory in root/pngs/
        images_directory = os.path.join(os.path.join(root, "pngs"), get_filename(pdf_path))

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


def pdfs_to_texts(root: str, verbose: bool = True, reuse: bool = True) -> None:
    """
    Look in root/pdfs, convert the pdfs to images (saved to root/pngs)
    and then extract the text from the images (saved to root/txts)
    :param root:
    :param verbose: if True, log progress to the console
    :param reuse: If False, recreate the image and txt file, even if those files already exist
    :return: None
    """
    pdf_paths = sorted(glob.glob(os.path.join(os.path.join(root, "pdfs"), "*.pdf")))

    for i, pdf_path in enumerate(pdf_paths, 1):
        file_id = get_filename(pdf_path)
        text_file_path = os.path.join(os.path.join(root, "txts"), file_id + ".txt")

        if not reuse or not os.path.exists(text_file_path):
            # The user doesn't want to reuse the already-processed files, or those files don't exist
            if verbose:
                print("Opening '{}' ({} out of {})".format(pdf_path, i, len(pdf_paths)))

            # Write the data to the appropriate text file
            with open(text_file_path, "w+") as text_file:
                text = get_text_from_pdf(pdf_path, os.path.join(root, "pngs"), verbose=verbose, reuse=reuse)
                text_file.writelines(text)
        else:
            # already-processed files exist, and the user wants to use them
            if verbose:
                print("'{}' Already exists. ({} out of {})".format(pdf_path, i, len(pdf_paths)))


def texts_to_jsons(root: str, stopwords_path: str, verbose: bool = True) -> None:
    """
    Look in root/txts/ and convert the raw text into json files with (word : frequency) pairs, saved to root/summaries
    :param root:
    :param stopwords_path: a path to a textfile, newline-deliminated list of words to exclude from the json file.
    :param verbose: if True, log progress to the console
    :rtype: None
    """
    txt_files = sorted(glob.glob(os.path.join(os.path.join(root, "txt"), "*.txt")))
    with open(stopwords_path, "r") as stopwords_txt:
        stopwords = set([word.strip() for word in stopwords_txt.readlines()])

    for i, txt_file in enumerate(txt_files, 1):
        if verbose:
            print("Converting {} to json ({} out of {})".format(txt_file, i, len(txt_files)))

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
        json_path = os.path.join(os.path.join(root, "summaries", "jsons"), get_filename(txt_file) + ".json")
        json_dict = {word: freq for word, freq in zip(clean_words, frequencies)}
        with open(json_path, "w+") as json_file:
            json.dump(json_dict, json_file, indent=2)


def json_to_graph(json_path: str, num_words: int = 50, verbose: bool = True) -> None:
    """
    Graph and save a bar chart with the frequencies of the words in json_path
    :param json_path: path to json file containing the words and their frequencies
    :param num_words: the maximum number of words to graph
    :param verbose: if True, log progress to the console
    :rtype: None, bar graphs are saved in corpus/summaries/bars/
    """
    if verbose:
        print("Graphing pie chart of {}".format(json_path))

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
    # plt.savefig(json_path.split(".")[0] + "-bar_chart.png")

    bar_directory = os.path.join(os.sep.join(json_path.split(os.sep)[:-1]), "bars")
    os.makedirs(bar_directory, exist_ok=True)
    bar_path = os.path.join(bar_directory, get_filename(json_path) + "-bar_chart.png")
    plt.savefig(bar_path)
    # plt.show()


def graph_memo_composition(root: str, memo_json_path: str, verbose: bool = True) -> None:
    """
    Graph and save a single pie chart, that shows the composition of the pdf represented by memo_json_path.
    The different categories represented by the wedges of the pie are the different json files found in topics/summaries
    :param memo_json_path:
    :param verbose:
    :rtype: None
    """
    if verbose:
        print("Graphing pie chart of {}".format(memo_json_path))

    with open(memo_json_path, "r") as jsonfile:
        data: dict = json.load(jsonfile)
    memo_words, memo_freqs = list(data.keys()), list(data.values())
    topic_scores = {}

    topic_paths = glob.glob(os.path.join(root, "summaries", "jsons", "*.json"))
    if len(topic_paths) == 0:
        print("No topic files found that match with '{}'. Graphing failed".format("topics/summaries/*.json"))
        return

    for topic_path in topic_paths:
        with open(topic_path, "r") as jsonfile:
            data: dict = json.load(jsonfile)

        topic_name = get_filename(topic_path)
        topic_words = list(data.keys())
        topic_scores[topic_name] = 0
        for memo_word, memo_freq in zip(memo_words, memo_freqs):
            if memo_word in topic_words:
                topic_scores[topic_name] += memo_freq

    print(topic_scores)
    sns.set_palette(sns.color_palette("BrBG", len(topic_paths)))

    fig, ax = plt.subplots(figsize=(10, 5), dpi=400, subplot_kw=dict(aspect="equal"))

    topic_scores = sorted([(topic, score) for topic, score in list(topic_scores.items())], key=lambda x: x[1])
    labels = [item[0] for item in topic_scores]
    numbers = [item[1] for item in topic_scores]

    patches, texts, autotexts = ax.pie(numbers,
                                       autopct='%1.1f%%',
                                       startangle=90,
                                       pctdistance=0.85,
                                       labels=labels,
                                       labeldistance=1.05,
                                       textprops={'fontsize': 8})

    # current_palette = sns.color_palette()
    ax.set_title("Composition of " + get_filename(memo_json_path).title())

    pie_directory = os.path.join(root, "summaries", "pies")
    os.makedirs(pie_directory, exist_ok=True)
    pie_path = os.path.join(pie_directory, get_filename(memo_json_path) + "-pie_chart.png")
    plt.tight_layout()
    plt.savefig(pie_path)


def create_test_topic(root, topic_id, total_unique_words=100):
    words = [topic_id + f"{i:0{len(str(total_unique_words))}}" for i in range(total_unique_words)]

    def freq_distribution(x):
        return math.ceil((0.4 * total_unique_words) / x)

    freqs = [math.ceil(freq_distribution(x + 1)) for x in range(total_unique_words)]

    json_dict = {word: freq for word, freq in zip(words, freqs)}
    json_path = os.path.join(root, "summaries", "jsons", "*.json")
    with open(json_path, "w+") as json_file:
        json.dump(json_dict, json_file, indent=2)


def create_test_memo(root="test_files/topics"):
    return
    # test_length = 20
    # word_freqs = {}
    # topics = glob.glob(f"{root}/summaries/*.json")
    # topic_wfs = {}
    # for topic in topics:
    #     with open(topic, "r") as json_file:
    #         topic_wfs.update(json.load(json_file))
    # for word in range(test_length):
    #
    #
    #
    # pass


def create_directory_structure(root: str):
    level1 = ["corpus", "topics"]
    level2 = ["pdfs", "pngs", "summaries", "txts"]

    for l1 in level1:
        for l2 in level2:
            if l2 is "summaries":
                os.makedirs(os.path.join(root, l1, l2, "bars"), exist_ok=True)
                os.makedirs(os.path.join(root, l1, l2, "pies"), exist_ok=True)
                os.makedirs(os.path.join(root, l1, l2, "jsons"), exist_ok=True)
            else:
                os.makedirs(os.path.join(root, l1, l2), exist_ok=True)


def developement_main() -> None:
    """
    Used for running and testing developement builds.
    This function may not be stable, and may corrupt the data.
    All stable features are available when calling the main() function.
    :rtype: None
    """
    sns.set()
    # pdfs_to_texts("corpus")
    # texts_to_jsons("corpus")
    # memo_json_paths = glob.glob("corpus/summaries/*.json")
    # for memo_json_path in memo_json_paths:
    #     json_to_graph(memo_json_path)
    #     graph_memo_composition(memo_json_path)

    for i in range(5):
        create_test_topic("test_files", chr(i + ord("a")), total_unique_words=20)


def main() -> None:
    """
    For first time users. Follow the instructions in the README.md and then run this funciton.
    This function will analyse the pdfs in corpus/pdfs and then produce graphs about the data
    :rtype: None
    """
    # Initialise the pretty graph maker
    sns.set()

    # Build json files about the memos
    pdfs_to_texts("corpus")
    texts_to_jsons("corpus")

    # Build json files about the topics
    pdfs_to_texts("topics")
    texts_to_jsons("topics")

    # Graph the data, saved to corpus/summaries/bars/ and corpus/summaries/pies/
    memo_json_paths = glob.glob("corpus/summaries/*.json")
    for memo_json_path in memo_json_paths:
        json_to_graph(memo_json_path)
        graph_memo_composition(memo_json_path)


if __name__ == '__main__':
    developement_main()
