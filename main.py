import glob

import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords

from QuestionPaper import QuestionPaper


def process(papers):
    # tokens = [[token for token in paper.text.split()] for paper in papers]
    tokens = [token for paper in papers for token in paper.text.split()]
    # clean_tokens = [token for token in tokens if token not in stopwords.words("english") and token.isalpha()]
    clean_tokens = []
    for token in tokens:
        if token.isalpha() and token not in stopwords.words("english") and "___" not in token:
            clean_tokens.append(token)
    clean_tokens += [tokens[i] + " " + tokens[i + 1] for i in range(len(tokens) - 1)]
    print(sorted(clean_tokens))

    plt.subplots_adjust(left=0.04, right=0.95, bottom=0.25, top=0.95)
    freq = nltk.FreqDist(clean_tokens)
    freq.plot(70, cumulative=False)

    # for paper in papers:
    #     tokens = [t for t in paper.text.split()]
    #     clean_tokens = [token for token in tokens if token not in stopwords.words("english")]
    #
    #     freq = nltk.FreqDist(clean_tokens)
    #     # for key, val in freq.items():
    #     #     print(str(key) + ':' + str(val))
    #     freq.plot(40, cumulative=False)


def main():
    filenames = glob.glob("pdfs/*.pdf")
    papers = [QuestionPaper(filename) for filename in filenames]
    process(papers)
    # for filename in filenames:
    #     paper = QuestionPaper(filename)
    #     papers.append(paper)
    # my_list = paper.parse()

    # if my_list is not None:
    #     with open(filename.split(".")[0] + ".md", "w") as file:
    #         file.writelines(my_list)


if __name__ == '__main__':
    main()
