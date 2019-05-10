import glob
import os
import re

import PyPDF2
import textract


class QuestionPaper(object):
    def __init__(self, filename):
        """
        Initialise the QuestionPaper class.
        QuestionPapers can be
            .read(): to get the data into variables
        :param filename: the filename + extension of the QuestionPaper to act on
        """
        self.filename = filename
        pdf = open(os.path.join(os.getcwd(), filename), 'rb')  # open the specified file in binary mode
        self.reader = PyPDF2.PdfFileReader(pdf)  # use PyPDF2 to read the pdf file
        self.data = []  # the list to eventually hold all the info about the QuestionPaper

        self.text = ""
        for i in range(self.reader.numPages):
            page = self.reader.getPage(i)
            self.text += str(page.extractText().encode("ascii", "ignore")) \
                .replace('\n', ' ') \
                .replace('\r', '')
        if self.text == "":
            self.text = textract.process(filename, method='tesseract', language='eng', encoding="utf8")
            self.text = self.text.replace("\n", " ")
            print("Using textract for file {}...".format(filename))
        else:
            print("Using PyPDF2 for file {}...".format(filename))

    def parse(self, regex_subquestion="(\\s\\([a-z]+\\)\\s+[A-Z])"):

        # Remove the underscores that are given as lines to answer on
        underscore_pattern = re.compile("_{3,}")
        end_of_question_pattern = re.compile("\\?")

        self.text = re.sub(underscore_pattern, "\n", self.text)
        self.text = re.sub(end_of_question_pattern, "\n", self.text)

        self.text = re.sub(re.compile("\s{4,}"), "", self.text)

        subquestion_pattern = re.compile(regex_subquestion)
        qs_and_as = subquestion_pattern.split(self.text)
        my_list = []
        for i, q_and_a in enumerate(qs_and_as):
            if i != 0 and i % 2 == 0:
                my_list.append(qs_and_as[i - 1] + q_and_a + "\n")

        subanswer_pattern = re.compile(regex_subquestion)
        qs_and_as = subquestion_pattern.split(self.text)
        # for item in my_list:

        if my_list:
            return my_list
        else:
            print("Parsing Error with file '{}' Change the regex({}) and try again".format(self.filename,
                                                                                           regex_subquestion))
            print("")
            return None

    def __repr__(self):
        output = []
        if self.data:
            for section in self.data:
                output.append("\n\n=================== New Section ===================\n\n")
                for question in section:
                    output.append("-------- New Question -------- \n")
                    output.append("\t{}...".format(question[:100]))
            return output
        else:
            return self.text.encode("ascii", "ignore")


def main():
    filenames = glob.glob("pdfs/*.pdf")
    for filename in filenames:
        paper = QuestionPaper(filename)
        my_list = paper.parse()
        if my_list is not None:
            with open(filename.split(".")[0] + ".txt", "w") as file:
                file.writelines(my_list)


if __name__ == '__main__':
    main()
