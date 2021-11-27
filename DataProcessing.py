import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, RegexpTokenizer
import string
from nltk.stem import WordNetLemmatizer
from nltk.probability import FreqDist
from wordcloud import WordCloud


class CommonWords:
        """
        This class tokenize text, extract the most common words in text and build word cloud
        """
    def __init__(self, file, quantity):
        self.file = file
        self.quantity = quantity
        self.stop = set(stopwords.words('english'))
        self.stop.update(set(stopwords.words('polish')))
        punctuation = list(string.punctuation)
        self.stop.update(punctuation)
        self.text = ''
        df = pd.read_csv(self.file, sep=';')
        for word in df.profile_text.values:
            self.text = self.text + word + ' '

    def common_words_to_df(self, filename):
        """
        Function to tokenize words in text and extract the most common words in text
        :param self: 
        :param filename: csv file
        :return: None
        """"
        tokenizer = RegexpTokenizer(r'\w+')
        text = tokenizer.tokenize(self.text)
        text = ' '.join(word for word in text)
        tokenized_word = word_tokenize(text)
        tokenized_word = [word.lower() for word in tokenized_word]
        filtered_word = []
        for word in tokenized_word:
            if word not in self.stop:
                filtered_word.append(word)

        for word in filtered_word:
            try:
                if isinstance(int(word), int):
                    filtered_word.remove(word)
            except:
                pass

        lem = WordNetLemmatizer()
        lem_words = []
        for w in filtered_word:
            lem_words.append(lem.lemmatize(w, 'n'))

        fdist = FreqDist(lem_words)
        most_common = fdist.most_common(self.quantity)
        common_words_df = pd.DataFrame(most_common, columns=['word', 'value'])
        common_words_df.to_csv(filename, index=False, sep=';')

    def word_cloud_to_file(self, name):
        """
        Function to build word cloud
        :param self:
        :param name: str
        :return:
        """
        wc = WordCloud(width=3000,
                       height=2000,
                       random_state=1,
                       background_color='black',
                       colormap='Set2',
                       collocations=False,
                       stopwords=self.stop).generate(self.text)
        wc.to_file(name)