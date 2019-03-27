import textract
import os
import PyPDF2

PATH = "file.pdf"
text = textract.process(PATH)

path = '.'

files = os.listdir(path)
for name in files:
    print(name)

print(text)
