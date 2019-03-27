import os
import PyPDF2
import re

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
# print(pdf_string)

questions = re.split("Question \\d+", pdf_string)  # split the string by any '(.)' types
data = []

"""
Regex: (\s\([a-z]\)\s+[A-Z])
* \\ to escape Python's go over of the string
* \s to match whitespace before the question
* ([a-z]) to match the start, middle and end of a '(a-z)' type question
* \s+[A-Z] to match a capital letter after the (), questions always start with capital letters
* all wrapped in a () to include the matched text in the output
"""
for question in questions:
    # TODO figure out how to include the matched text in the split
    data.append(re.split("(\\s\\([a-z]\\)\\s+[A-Z])", question))

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
        print ("\t" + question)
