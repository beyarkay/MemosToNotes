import os
import re

import PyPDF2


def split_keep_splitter(text, splitter):
    splitter_pattern = re.compile("({})".format(splitter))
    splits = splitter_pattern.split(text)

    if len(splits) != 0:
        result = [splits[0]]
        for i, split in enumerate(splits[:-1]):
            if i % 2 == 0 and i != 0:
                result.append(splits[i - 1] + split)
        return result
    else:
        return []


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

        self.text = ""

        # for i in range(self.reader.numPages):
        #     page = self.reader.getPage(i)
        #     self.text += str(page.extractText().encode("ascii", "ignore"))

        if self.text == "":
            self.text = textract.process(filename, method='tesseract', language='eng', encoding="utf8")
            print("Using textract for file {}...".format(filename))
        else:
            print("Using PyPDF2 for file {}...".format(filename))

        self.text = self.text.replace('\n', ' ').replace('\r', '')
        self.text = re.sub(re.compile("_{3,}"), "\n", self.text)
        # with open("memos/debug_text.txt", "w") as debug_file:
        #     # insert a newline every 120 characters for readability
        #     debug_file.write(re.sub("(.{120})", "\\1\n", self.text, 0, re.DOTALL))

    def parse(self, regex_subquestion="\\([a-z]+\\)\\s+[A-Z]"):
        end_of_question_pattern = re.compile("\\?")

        self.text = re.sub(end_of_question_pattern, "?\n* ", self.text)

        self.text = re.sub(re.compile("\s{4,}"), " ", self.text)

        # self.text = re.sub(re.compile("Question [0-9]+\\s"), "\n# Question something or other\n", self.text)
        split_questions = re.split(re.compile("(Question [0-9]+\\s)"), self.text)
        for i, question in enumerate(split_questions):
            if "Question" in question[:15]:
                split_questions[i] = "# " + question

        self.text = "\n".join(split_questions)

        subquestions = split_keep_splitter(self.text, regex_subquestion)
        self.text = "\n\n".join(subquestions)

        if subquestions:
            return [line + "\n\n" for line in subquestions]
        else:
            print("Parsing Error with file '{}' Change the regex({}) and try again\n".format(self.filename,
                                                                                             regex_subquestion))
            return None

    def __repr__(self):
        return self.text.encode("ascii", "ignore")
