import pandas as pd
import numpy as np
import os
import re
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
import sys
import logging

class DataProcessor:
    def __init__(self, input_file: str, text_files_dir: str, stop_words_dir: str, master_dictionary_dir: str):
        # Initialize the DataProcessor object with the given input file, text files directory, stop words directory and master dictionary directory
        self.input_file = input_file
        self.text_files_dir = text_files_dir
        self.stop_words_dir = stop_words_dir
        self.all_stop_words = set()
        self.master_dictionary_dir = master_dictionary_dir
        self.df = None
    
    def create_directories(self):
        # If text files directory does not exist, create the directory
        if not os.path.exists(self.text_files_dir):
            os.makedirs(self.text_files_dir)

    def process_data(self):
        try:
            self.load_data()
            self.load_stop_words()
            self.extract_and_save_text_data()
            self.calculate_sentiment_scores()
            self.calculate_output_variables()
            logging.info('Data processing steps completed')
        except Exception as e:
            logging.exception(f'Error occurred during processing the data: {e}')

    def load_stop_words(self):
        # Load the stop words from stop words directory files
        for file in os.listdir(self.stop_words_dir):
            with open(os.path.join(self.stop_words_dir, file), 'r', encoding='ISO-8859-1') as f:
                self.all_stop_words.update(set(f.read().splitlines()))

    def load_data(self):
        # Load the data from the input file into a Pandas DaraFrame
        try:
            self.df = pd.read_excel(self.input_file)
            logging.info('Input file format data loaded successfully inside the pandas dataframe')
        except Exception as e:
            logging.critical(f'Error occurred while loading the input file inside the pandas dataframe: {e}')

    def extract_and_save_text_data(self):
        # Set the base URL and headers for making HTTP requests
        # base_url = 'https://insights.blackcoffer.com/'
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8',
            'accept-encoding': 'gzip, deflate, br'
        }
        # Creating a requests sesstion
        # sess = requests.Session()

        for index, row in self.df.iterrows():
            self.create_directories()
            url = row['URL']
            url_id = row['URL_ID']
            try:
                response = requests.get(url=url, headers=headers)
                # cookies = dict(response.cookies)
                if response.status_code == 200:
                    try:
                        # Parse the HTML content of the response using BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # Find the title and article text
                        title = soup.find('h1').get_text()
                        article = " ".join([p.get_text() for p in soup.find_all('p')])

                        file_name = os.path.join(self.text_files_dir, str(url_id) + '.txt')
                        with open(file_name, 'w', encoding='utf-8') as file:
                            file.write(title + ": " + article)
                        logging.info(f'Text data extracted and saved for URL_ID: {url_id}')

                    except Exception as e:
                        logging.exception(f'An error occurred while parsing HTML content for URL_ID: {url_id}: {e}')
                else:
                    logging.error(f'Received HTTP status code {response.status_code} for URL_ID: {url_id}')
            except Exception as e:
                logging.warning(f'Error occurred for URL_ID: {url_id}: {e}')

    def calculate_sentiment_scores(self):
        # Initialize sets to store positive and negative words
        pos_words = set()
        neg_words = set()
        
        # Load the positive and negative words from the master dictionary directory files
        for file in os.listdir(self.master_dictionary_dir):
            if file == 'positive-words.txt':
                with open(os.path.join(self.master_dictionary_dir, file), 'r', encoding='ISO-8859-1') as f:
                    pos_words.update(f.read().splitlines())
            else:
                with open(os.path.join(self.master_dictionary_dir, file), 'r', encoding='ISO-8859-1') as f:
                    neg_words.update(f.read().splitlines())

        # Initialize lists to store the sentiment scores
        positive_score = []
        negative_score = []
        polarity_score = []
        subjectivity_score = []

        for i, row in self.df.iterrows():
            self.create_directories()
            url_id = row['URL_ID']
            url = row['URL']
            text_file = f"{url_id}.txt"
            text_file_path = os.path.join(self.text_files_dir, text_file)

            # Check if the text file exists for URL_ID
            if not os.path.exists(text_file_path):
                positive_score.append(np.nan)
                negative_score.append(np.nan)
                polarity_score.append(np.nan)
                subjectivity_score.append(np.nan)
                continue
            
            try:
                with open(text_file_path, 'r', encoding='ISO-8859-1') as f:
                    text = f.read()
                    # Tokenize the text and filter out stop words
                    tokens = word_tokenize(text)
                    filtered_text = [item for item in tokens if item.lower() not in self.all_stop_words]
                    # Count the number of positive and negative words in the filtered text
                    positive_words = [word for word in filtered_text if word.lower() in pos_words]
                    positive_score.append(len(positive_words))
                    negative_words = [word for word in filtered_text if word.lower() in neg_words]
                    negative_score.append(len(negative_words))
                    # Calculate the polarity and subjectivity score
                    polarity_score.append((positive_score[i] - negative_score[i]) / ((positive_score[i] + negative_score[i] + 0.000001)))
                    subjectivity_score.append((polarity_score[i] + negative_score[i]) / ((len(filtered_text)) + 0.000001))
                    logging.info(f"Output variables calculated for URL_ID: {url_id}")
            except Exception as e:
                logging.exception(f"An error occurred while calculating output variables for URL_ID: {url_id}: {e}")

        # Add the sentiment scores to the DataFrame as new columns
        self.df['POSITIVE SCORE'] = positive_score
        self.df['NEGATIVE SCORE'] = negative_score
        self.df['POLARITY SCORE'] = polarity_score
        self.df['SUBJECTIVITY SCORE'] = subjectivity_score

    def calculate_output_variables(self):
        # Initialize lists to store the output variables
        avg_sentence_length = []
        percentage_of_complex_words = []
        fog_index = []
        avg_num_words_per_sentence = []
        complex_word_count = []
        word_count = []
        syllable_per_word = []
        personal_pronouns = []
        avg_word_length = []

        def count_syllables(word):
            vowels = 'aeiou'
            # Count the number of vowels in the word and return the count
            syllable_count = 0
            for letter in word:
                if letter.lower() in vowels:
                    syllable_count += 1
            return syllable_count

        for i, row in self.df.iterrows():
            # Get the URL ID and URL from the current row
            url_id = row['URL_ID']
            url = row['URL']
            text_file = f"{url_id}.txt"
            text_file_path = os.path.join(self.text_files_dir, text_file)

            if not os.path.exists(text_file_path):
                avg_sentence_length.append(np.nan)
                percentage_of_complex_words.append(np.nan)
                fog_index.append(np.nan)
                avg_num_words_per_sentence.append(np.nan)
                complex_word_count.append(np.nan)
                word_count.append(np.nan)
                syllable_per_word.append(np.nan)
                personal_pronouns.append(np.nan)
                avg_word_length.append(np.nan)
                continue

            with open(text_file_path, 'r', encoding='ISO-8859-1') as f:
                text = f.read()
                # Remove all non-word characters except spaces and periods
                text = re.sub(r'[^\w\s.]', '', text)
                # Split the text into sentences and count the number of sentences
                sentences = text.split('.')
                num_sentences = len(sentences)
                # Tokeinize the text and count the number of words
                words = word_tokenize(text)
                num_words = len(words)
                # Count the number of comples words (words with more than 2 syllables)
                complex_words = [word for word in words if count_syllables(word) > 2]
                num_complex_words = len(complex_words)
                # Calculate the average sentence length and percentage of complex words
                avg_sentence_length.append(num_words / num_sentences)
                percentage_of_complex_words.append(num_complex_words / num_words)
                # Calculate the fog index
                fog_index.append(0.4 * (avg_sentence_length[-1] + percentage_of_complex_words[-1]))
                avg_num_words_per_sentence.append(num_words / num_sentences)
                complex_word_count.append(num_complex_words)
                word_count.append(num_words)
                syllable_per_word.append(sum(count_syllables(word) for word in words) / num_words)
                # Count the number of personal pronouns in the text
                personal_pronouns.append(self.count_personal_pronouns(words))
                # Calculate the average word length
                avg_word_length.append(sum(len(word) for word in words) / num_words)

        # Add the output variable to the DataFrame as new columns
        self.df['AVG SENTENCE LENGTH'] = avg_sentence_length
        self.df['PERCENTAGE OF COMPLEX WORDS'] = percentage_of_complex_words
        self.df['FOG INDEX'] = fog_index
        self.df['AVG NUMBER OF WORDS PER SENTENCE'] = avg_num_words_per_sentence
        self.df['COMPLEX WORD COUNT'] = complex_word_count
        self.df['WORD COUNT'] = word_count
        self.df['SYLLABLE PER WORD'] = syllable_per_word
        self.df['PERSONAL PRONOUNS'] = personal_pronouns
        self.df['AVG WORD LENGTH'] = avg_word_length

    def count_personal_pronouns(self, words):
        personal_pronouns = ['i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours']
        pronoun_count = 0
        # Count the number of personal pronouns in the given list of words and return the count
        for word in words:
            if word.lower() in personal_pronouns:
                pronoun_count += 1
        return pronoun_count

    def save_output_csv(self, output_file):
        # Define the columns to include in the output CSV file
        # These columns are as per 'Output Data Structure' file
        columns = ['URL_ID', 'URL', 'POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY SCORE', 'SUBJECTIVITY SCORE',
                   'AVG SENTENCE LENGTH', 'PERCENTAGE OF COMPLEX WORDS', 'FOG INDEX',
                   'AVG NUMBER OF WORDS PER SENTENCE', 'COMPLEX WORD COUNT', 'WORD COUNT',
                   'SYLLABLE PER WORD', 'PERSONAL PRONOUNS', 'AVG WORD LENGTH']
        
        # Save the DataFrame to a CSV file using the specified columns
        try:
            self.df.to_csv(output_file, index=False, columns=columns)
            logging.critical(f'Output file saved successfully')
        except Exception as e:
            logging.exception(f'Error occurred while saving the output file')


if __name__ == '__main__':
    logging.basicConfig(filename='blackcoffer_logs.log', level=logging.INFO, format='%(asctime)s : %(levelname)s : %(message)s', filemode='a')
    input_file = 'Input.xlsx'
    text_files_dir = os.path.join(os.getcwd(), 'text_files')
    stop_words_dir = os.path.join(os.getcwd(), 'StopWords')
    master_dictionary_dir = os.path.join(os.getcwd(), 'MasterDictionary')
    output_file = 'output.csv'

    processor = DataProcessor(input_file, text_files_dir, stop_words_dir, master_dictionary_dir)
    processor.process_data()
    processor.save_output_csv(output_file)
    print('Output file saved successfully.')
