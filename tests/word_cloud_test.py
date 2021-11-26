import os
from os import path

import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS

# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

# Read the whole text.
text = open(path.join(d, "constitution.txt")).read()
# print(text)

# create the wordcloud object
# nltk.download('stopwords') # download only once
stop_words_sp = set(stopwords.words('spanish'))
wordcloud = WordCloud(stopwords=stop_words_sp, collocations=False).generate(text)

############################################################################
############################################################################

# create a dictionary of word frequencies
text_dictionary = wordcloud.process_text(text)
print(text_dictionary)
# sort the dictionary
word_freq = {
    k: v
    for k, v in sorted(text_dictionary.items(), reverse=True, key=lambda item: item[1])
}

# use words_ to print relative word frequencies
rel_freq = wordcloud.words_

# print results
print(list(word_freq.items())[:10])
print(list(rel_freq.items())[:10])
