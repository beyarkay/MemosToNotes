import os
import PyPDF2

ABSOLUTE_PATH = "/Users/boydkane/PycharmProjects/MemosToNotes"
FILE_NAME_WITH_EXTENSION = "file.pdf"
FILE_PATH = os.path.join(ABSOLUTE_PATH, FILE_NAME_WITH_EXTENSION)

pdf = open(FILE_PATH, 'rb')
reader = PyPDF2.PdfFileReader(pdf)
print(reader.getDocumentInfo())
for i in range(reader.numPages):
    page = reader.getPage(i)
    print(page.extractText())