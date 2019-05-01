import os
import re

import PyPDF2

"""

"""


# TODO Create Docstring
# TODO Finish Class for QuestionPaper objects

class QuestionPaper(object):
    def __init__(self, filename):
        """
        Initialise the QuestionPaper class.
        QuestionPapers can be
            .read(): to get the data into variables
        :param filename: the filename + extension of the QuestionPaper to act on
        """
        FILE_NAME_WITH_EXTENSION = filename
        ABSOLUTE_PATH = os.getcwd()
        self.FILE_PATH = os.path.join(ABSOLUTE_PATH, FILE_NAME_WITH_EXTENSION)  # calculate the absolute file path
        pdf = open(self.FILE_PATH, 'rb')  # open the specified file in binary mode
        self.reader = PyPDF2.PdfFileReader(pdf)  # use PyPDF2 to read the pdf file
        self.data = []  # the list to eventually hold all the info about the QuestionPaper

        """
        Explanation of the regex used: 
        Note: All backslashes have to be doubled up, as both python and regex uses them as escape characters
            (\s\([a-z]\)\s+[A-Z])   To match the start of an actual question
                * \s to match whitespace before the question
                * ([a-z]) to match the start, middle and end of a '(a-z)' type question
                * \s+[A-Z] to match a capital letter after the (), questions always start with capital letters
                
            Question \d+"   To match the start of a Computer Science Section header
                * Question to match with any CSC question title.
                * \d+ to match with any number of digits (at least one)
                * Examples:
                    Question 2
                    Question 12
                    Question 0
        """
        self.REGEX_SECTION = "Question \\d+"  # TODO expand this out to also catch other Section headers
        self.REGEX_QUESTION = "\\s\\([a-z]\\)\\s+[A-Z]"

    def read(self):
        pdf_string = ""

        # Convert the reader object into one string (pdf_string) with all the data from the pdf
        for i in range(self.reader.numPages):
            page = self.reader.getPage(i)
            pdf_string += page.extractText()

        section = re.split(self.REGEX_SECTION, pdf_string)  # split the pdf string by its section headers


        error go through the code below
        for question in section:    # split the sections into different questions
            pattern = re.compile(self.REGEX_QUESTION)  # compile the regex into a patter to match with
            # split_locations contains where each question starts / ends
            split_locations = [match.start() for match in pattern.finditer(question)]
            split_locations.insert(0, 0)  # prepend a zero so as to not skip the beginning part
            temp = []
            for i in range(len(split_locations) - 1):
                temp.append(question[split_locations[i]:split_locations[i + 1]])
            self.data.append(temp)

            # TODO delete the unreadable list comprehension below once the above code is tested
            # self.data.append(
            #     [question[split_locations[i]:split_locations[i + 1]] for i in range(len(split_locations) - 1)])

            for section in self.data:
                for i in range(len(section)):
                    if len(section[i]) < 7 and i + 2 < len(section):
                        section[i + 1] = section[i] + section[i + 1]
                    for i in range(len(self.data)):
                        self.data[i] = [question for question in self.data[i] if len(question) >= 7]

    def __repr__(self):
        output = []
        for section in self.data:
            output.append("\n\n=================== New Section ===================\n\n")
            for question in section:
                output.append("-------- New Question -------- \n")
                output.append("\t{}...".format(question[
                                               :100]))  # TODO Sort out the error: UnicodeEncodeError: 'ascii' codec can't encode character u'\ufb01' in position 41: ordinal not in range(128)
        for line in output:
            print (line)

# ABSOLUTE_PATH = "/Users/boydkane/PycharmProjects/MemosToNotes"
# FILE_NAME_WITH_EXTENSION = "file1.pdf"
# FILE_PATH = os.path.join(ABSOLUTE_PATH, FILE_NAME_WITH_EXTENSION)
#
# pdf = open(FILE_PATH, 'rb')
# reader = PyPDF2.PdfFileReader(pdf)
# print(reader.getDocumentInfo())
# pdf_string = ""
# for i in range(reader.numPages):
#     page = reader.getPage(i)
#     pdf_string += page.extractText()
# print(pdf_string)
#
# questions = re.split("Question \\d+", pdf_string)
# data = []
#
# REGEX = "\\s\\([a-z]\\)\\s+[A-Z]"
#
# for question in questions:
#     pattern = re.compile(REGEX)
#     split_locations = [match.start() for match in pattern.finditer(question)]
#     split_locations.insert(0, 0)
#     # split the question string based off of the values in split location
#     data.append([question[split_locations[i]:split_locations[i + 1]] for i in range(len(split_locations) - 1)])
#
# for section in data:
#     for i in range(len(section)):
#         if len(section[i]) < 7 and i + 2 < len(section):
#             section[i + 1] = section[i] + section[i + 1]
# for i in range(len(data)):
#     data[i] = [question for question in data[i] if len(question) >= 7]
#
# for section in data:
#     print ("\n\n=================== New Section ===================\n\n")
#     for question in section:
#         print ("-------- New Question -------- \n")
#         print ("\t{}...".format(question[
#                                 :100]))  # TODO Sort out the error: UnicodeEncodeError: 'ascii' codec can't encode character u'\ufb01' in position 41: ordinal not in range(128)
