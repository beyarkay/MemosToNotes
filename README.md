# MemosToNotes

MemosToNotes is a Python program designed for students that takes in a corpus of exam paper memorandums, as well as lecture notes for each topic that might be tested on the exam.

MemosToNotes then analyses the exams and lecture notes, giving the users useful information about the coposition of each exam paper.

![My image](readme-files/pie_2018.png) ![My image](readme-files/pie_2018.png)


## Usage

1. Download the project to your local machine
2. Install all the packages and modules in `requirements.txt`:
    * seaborn - For styling the charts
    * numpy - For general data manipulation
    * matplotlib - For plotting the data
    * wand - For converting a multi-page pdf into a directory of images 
    * Pillow - For opening the images so pytesseract can work with them
    * pytesseract - a python wrapper for tesseract
        * tesseract -  the OCR engine by Google. This is not a python package, but is required for pytesseract to work
3. Open main.py, and change the following line:
    ```
    def get_text_from_pdf(...):
        ...
        # Make sure pytesseract knows where tesseract is stored
        # CHANGE THIS PATH to be the absolute path to the tesseract unix executable file
        pytesseract.pytesseract.tesseract_cmd =  '/anaconda3/envs/MemosToNotes3/bin/tesseract'
    ```
4. Add your own pdf exam paper memos to `MemosToNotes/corpus/pdfs/`
    * Each exam paper should be exactly one pdf.
    * The best results come from uploading the memos and not just the question papers (although uploading the question papers will work)
5. Add your own pdf lecture notes to `MemosToNotes/topics/pdfs/`
    * The lecture notes have to be pdfs
    * Each document in `MemosToNotes/topics/pdfs/` will be considered as a completely separate topic, so don't upload more than one set of lecture notes per topic.
6. Run the `run_from_nothing()` method in the main.py file
7. The resulting graphs will be stored in `MemosToNotes/corpus/summaries/bars` and `MemosToNotes/corpus/summaries/pies`

