import textract
PATH = "file.pdf"
text = textract.process(PATH)
# My new change
print(text)