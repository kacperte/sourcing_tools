import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, RegexpTokenizer
import string
from nltk.probability import FreqDist
from wordcloud import WordCloud


class CommonWords:
    """
    This class tokenize text, extract the most common words in text and build word cloud
    """

    def __init__(self, quantity):
        """
        Constructor
        :param quantity: int
        """

        self.quantity = quantity

        # Adding english/polish stopwords and punctuation  marks to dict
        self.stop = set(stopwords.words('english'))
        self.stop.update(set(stopwords.words('polish')))
        punctuation = list(string.punctuation)
        self.stop.update(punctuation)
        self.text = ''

    def common_words_to_df(self, file):
        """
        Function to tokenize words in text and extract the most common words in text
        :param self:
        :return: None
        """
        print('## Initzilize NLTK (Natural Language Toolkit)')
        print(f'## Prepering {self.quantity} most common words in text')

        # Open csv file
        df = pd.read_csv(file, sep=';')

        # Marge text from df to variable (str)
        for word in df.profile_text.values:
            self.text = self.text + word + ' '

        # Tokenize text
        tokenizer = RegexpTokenizer(r'\w+')
        text = tokenizer.tokenize(self.text)

        # Tokenized text
        text = ' '.join(word for word in text)
        tokenized_word = word_tokenize(text)
        tokenized_word = [word.lower() for word in tokenized_word]
        filtered_word = []

        # Filtering text (excluding stopwords)
        for word in tokenized_word:
            if word not in self.stop:
                filtered_word.append(word)

        for word in filtered_word:
            try:
                if isinstance(int(word), int):
                    filtered_word.remove(word)
            except:
                pass

        # Build common words
        fdist = FreqDist(filtered_word)

        # Select n words from dict - n is quantity variable in class
        most_common = fdist.most_common(self.quantity)

        # Build df and extract to csv
        common_words_df = pd.DataFrame(most_common, columns=['word', 'value'])
        common_words_df.to_csv('cw.csv', index=False, sep=';')
        print('## Success')

    def word_cloud_to_file(self):
        """
        Function to build word cloud and save it to .png format
        :param self:
        :param name: str
        :return:
        """
        print(f'## Prepering word cloud')

        # WC instance
        wc = WordCloud(width=3000,
                       height=2000,
                       random_state=1,
                       background_color='black',
                       colormap='Set2',
                       collocations=False,
                       stopwords=self.stop).generate(self.text)

        # Save to .png
        wc.to_file('wc.png')
        print('## Success')
