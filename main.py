import textract
PATH = "file.pdf"
text = textract.process(PATH)
print(text)