from DataProcessing import CommonWords
from BrowserBot import Browser


if __name__ == "__main__":
    query = r"site:linkedin.com/in/ OR site:linkedin.com/pub/ ""Google Ads"" Łódź SEO"
    browser_instance = Browser(username='kozuch-90@wp.pl',
                               password='kaczka12',
                               query=query,
                               n_pages=2
                               )
    browser_instance.talent_mapping()
    common_words = CommonWords('1.csv', 30)
    common_words.common_words_to_df('ads_cw2.csv')
    common_words.word_cloud_to_file('ads.cw2.png')




