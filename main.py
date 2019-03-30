import os
import PyPDF2
import re

"""

"""


# TODO Create Docstring
# TODO Create Class for QuestionPaper objects

class QuestionPaper(object):
    def __init__(self, filename):
        FILE_NAME_WITH_EXTENSION = filename
        ABSOLUTE_PATH = os.getcwd()
        self.FILE_PATH = os.path.join(ABSOLUTE_PATH, FILE_NAME_WITH_EXTENSION)
        pdf = open(self.FILE_PATH, 'rb')
        self.reader = PyPDF2.PdfFileReader(pdf)

        """
        Regex: (\s\([a-z]\)\s+[A-Z])
        * \\ to escape Python's go over of the string
        * \s to match whitespace before the question
        * ([a-z]) to match the start, middle and end of a '(a-z)' type question
        * \s+[A-Z] to match a capital letter after the (), questions always start with capital letters
        """
        self.REGEX_SECTION = "Question \\d+"
        self.REGEX_QUESTION = "\\s\\([a-z]\\)\\s+[A-Z]"

    def read(self):
        pdf_string = ""

        # Convert the reader object into one string with all the data
        for i in range(self.reader.numPages):
            page = self.reader.getPage(i)
            pdf_string += page.extractText()

        questions = re.split(self.REGEX_SECTION, pdf_string)  # split the string by any '(.)' types
        data = []

        for question in questions:
            pattern = re.compile(REGEX)
            split_locations = [match.start() for match in pattern.finditer(question)]
            split_locations.insert(0, 0)
            # split the question string based off of the values in split location
            data.append([question[split_locations[i]:split_locations[i + 1]] for i in range(len(split_locations) - 1)])


ABSOLUTE_PATH = "/Users/boydkane/PycharmProjects/MemosToNotes"
FILE_NAME_WITH_EXTENSION = "file1.pdf"
FILE_PATH = os.path.join(ABSOLUTE_PATH, FILE_NAME_WITH_EXTENSION)

pdf = open(FILE_PATH, 'rb')
reader = PyPDF2.PdfFileReader(pdf)
print(reader.getDocumentInfo())
pdf_string = ""
for i in range(reader.numPages):
    page = reader.getPage(i)
    pdf_string += page.extractText()
print(pdf_string)

questions = re.split("Question \\d+", pdf_string)
data = []

REGEX = "\\s\\([a-z]\\)\\s+[A-Z]"

for question in questions:
    pattern = re.compile(REGEX)
    split_locations = [match.start() for match in pattern.finditer(question)]
    split_locations.insert(0, 0)
    # split the question string based off of the values in split location
    data.append([question[split_locations[i]:split_locations[i + 1]] for i in range(len(split_locations) - 1)])

for section in data:
    for i in range(len(section)):
        if len(section[i]) < 7 and i + 2 < len(section):
            section[i + 1] = section[i] + section[i + 1]
for i in range(len(data)):
    data[i] = [question for question in data[i] if len(question) >= 7]

for section in data:
    print ("\n\n=================== New Section ===================\n\n")
    for question in section:
        print ("-------- New Question -------- \n")
        print ("\t{}...".format(question[
                                :100]))  # TODO Sort out the error: UnicodeEncodeError: 'ascii' codec can't encode character u'\ufb01' in position 41: ordinal not in range(128)
