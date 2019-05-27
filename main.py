import glob
import os

import nltk
import pytesseract
from PIL import Image as PILImage
from nltk.corpus import stopwords
from wand.image import Image as WandImage


def process(papers):
    # # tokens = [[token for token in paper.text.split()] for paper in papers]
    # tokens = [token for paper in papers for token in paper.text.split()]
    # # clean_tokens = [token for token in tokens if token not in stopwords.words("english") and token.isalpha()]
    # clean_tokens = []
    # for token in tokens:
    #     if token.isalpha() and token not in stopwords.words("english") and "___" not in token:
    #         clean_tokens.append(token)
    # clean_tokens += [tokens[i] + " " + tokens[i + 1] for i in range(len(tokens) - 1)]
    # # print(sorted(clean_tokens))
    #
    # plt.subplots_adjust(left=0.04, right=0.95, bottom=0.25, top=0.95)
    # freq = nltk.FreqDist(clean_tokens)
    # print("Drawing graph. Close Graph to continue with the processing")
    # freq.plot(70, cumulative=False)

    frequencies = []
    for paper in papers:
        print("Processing paper: {}...".format(paper.filename))
        tokens = [t for t in paper.text.split()]
        clean_tokens = [token for token in tokens if token not in stopwords.words("english")]

        freq = nltk.FreqDist(clean_tokens)
        filename = paper.filename.split(".")[0].split("/")[1] + ".txt"
        with open("frequencies/" + filename, "w") as freq_file:
            for key, val in sorted(freq.items(), key=lambda x: x[1], reverse=True):
                freq_file.write(str(key) + ' : ' + str(val) + "\n")


def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    Usage instrucitons: https://anaconda.org/jiayi_anaconda/pytesseract
    """
    # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
    pytesseract.pytesseract.tesseract_cmd = '/anaconda3/envs/MemosToNotes3/bin/tesseract'

    with WandImage(filename=filename, resolution=300) as image:
        image.compression_quality = 99
        name_sans_extension = filename.split(os.sep)[-1].split(".")[0]
        jpeg_filename = name_sans_extension + ".jpeg"
        if not os.path.isdir(os.path.join("images", name_sans_extension)):
            os.mkdir(os.path.join("images", name_sans_extension))

        jpeg_path = os.path.join("images", name_sans_extension, jpeg_filename)
        image.save(filename=jpeg_path)

    filenames = glob.glob(os.path.join("images", name_sans_extension, "*.jpeg"))
    text = []
    for filename in filenames:
        text.append(pytesseract.image_to_string(PILImage.open(filename)))
    return text


def main():
    print(ocr_core('pdfs/ocr_1.pdf'))
    # filenames = glob.glob("pdfs/*.pdf")
    # filenames = filenames[:5]  # While testing, limit the number of files processed
    # papers = [QuestionPaper(filename) for filename in filenames]
    # process(papers)
    # for filename in filenames:
    #     paper = QuestionPaper(filename)
    #     papers.append(paper)
    # my_list = paper.parse()
    #
    # if my_list is not None:
    #     with open(filename.split(".")[0] + ".md", "w") as file:
    #         file.writelines(my_list)


if __name__ == '__main__':
    main()
