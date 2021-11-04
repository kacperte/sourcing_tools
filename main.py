from DataProcessing import CommonWords
from BrowserBot import Browser


if __name__ == "__main__":
    query = r"site:linkedin.com/in/ OR site:linkedin.com/pub/ ""Google Ads"" Łódź"
    browser_instance = Browser(username='kozuch-90@wp.pl',
                               password='kaczka12',
                               query=query,
                               n_pages=2
                               )
    browser_instance.talent_mapping()

''' browser_instance.extract_text_from_profile_to_df('automatycy_lodz.csv')
    common_words = CommonWords('automatycy_lodz.csv', 50)
    common_words.common_words_to_df('automatycy_lodz_CW2.csv')
    common_words.word_cloud_to_file('automatycy_lodz2.png')'''




