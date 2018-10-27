import pandas as pd
import json
import re
import random
import nltk
from nltk.corpus import stopwords
import gensim
from sklearn.metrics.pairwise import cosine_similarity

import warnings
warnings.simplefilter('ignore')


class TextProcessing:
    def __init__(self, language):

        path = './Data/'

        # Pre-processing data: convert json file into data frame
        data_tokens = self.preprocessing_data(path)

        # Greeting function
        GREETING_INPUTS = ("hello", "hi", "greetings", "hello i need help", "good day", "hey", "i need help",
                           "greetings")
        GREETING_RESPONSES = ["Good day, How may i of help?", "Hello, How can i help?", "Hello",
                              "I am glad! You are talking to me."]

        # Retrieve sub-set of data frame based on specified language
        data_language = data_tokens[data_tokens['Class'] == language]
        data_language = pd.DataFrame({'Question': list(data_language['Question']),
                                      'Question_Tokens': list(data_language['Question_Tokens']),
                                      'Answer': list(data_language['Answer']),
                                      'Class': list(data_language['Class']),
                                      'Question_Vectors': list(data_language['Question_Vectors']),
                                      'Average_Pooling': list(data_language['Average_Pooling'])})

        # Read word2vec model
        word2vec_pickle_path = path + 'stackoverflow_word2vec_' + language + '.bin'
        model = gensim.models.KeyedVectors.load(word2vec_pickle_path)

        # self.flag_query = True
        self.path = path
        self.GREETING_INPUTS = GREETING_INPUTS
        self.GREETING_RESPONSES = GREETING_RESPONSES
        self.data_language = data_language
        self.model = model

    def pre_process(self, questions):
        stop_words = stopwords.words("english")

        # Remove non english words
        questions = [re.sub('[^a-z(c++)(c#)]', ' ', x.lower()) for x in questions]
        # Tokenize
        questions_tokens = [nltk.word_tokenize(t) for t in questions]
        # Removing Stop Words
        questions_stop = [[t for t in tokens if (t not in stop_words)
                           and (3 < len(t.strip()) < 15)] for tokens in questions_tokens]

        questions_stop = pd.Series(questions_stop)
        return questions_stop

    def preprocessing_data(self, path):

        stackoverflow_path = path + 'StackOverflow_Word2Vec.json'

        with open(stackoverflow_path) as file:
            reader = json.load(file)

            classes = []
            questions = []
            questions_tokens = []
            answers = []
            question_lengths = []
            question_vectors = []
            average_pooling = []

            for row in reader:
                classes.append(row['Class'])
                questions.append(row['Question'])
                questions_tokens.append(row['Question_Tokens'].split())
                answers.append(row['Answer'])
                question_lengths.append(row['Question_Length'])
                question_vectors.append(row['Question_Vectors'])
                average_pooling.append(row['Average_Pooling'])

            data_tokens = pd.DataFrame({'Class': classes,
                                        'Question': questions,
                                        'Question_Tokens': questions_tokens,
                                        'Answer': answers,
                                        'Question_Length': question_lengths,
                                        'Question_Vectors': question_vectors,
                                        'Average_Pooling': average_pooling})
        return data_tokens

    def greeting(self, sentence):
        for word in sentence.split():
            if word.lower() in self.GREETING_INPUTS:
                return random.choice(self.GREETING_RESPONSES), "", []

    def talk_to_jarvis(self, sentence, data_language, model):

        # Pre-processing of user input, tokenize, followed by stop word removal
        sentence_pp = self.pre_process(pd.Series(sentence))

        cosines = []
        try:
            # Get vectors and average pooling
            question_vectors = []
            for token in sentence_pp:
                try:
                    vector = model[token]
                    question_vectors.append(vector)
                except:
                    continue
            question_ap = list(pd.DataFrame(question_vectors[0]).mean())

            # Calculate cosine similarity
            for t in data_language['Average_Pooling']:
                if t is not None and len(t) == len(question_ap):
                    val = cosine_similarity([question_ap], [t])
                    cosines.append(val[0][0])
                else:
                    cosines.append(0)
        except:
            pass

        # If not in the topic trained
        if len(cosines) == 0:
            not_understood = "Apology, I do not understand. Can you rephrase?"
            return not_understood, "", []

        else:
            # Sort similarity
            index_s = []
            score_s = []
            for i in range(len(cosines)):
                x = cosines[i]
                if x >= 0.9:
                    index_s.append(i)
                    score_s.append(cosines[i])

            reply_indexes = pd.DataFrame({'index': index_s, 'score': score_s})
            reply_indexes = reply_indexes.sort_values(by="score", ascending=False)

            # Find Top-6 Questions, Answers and Scores
            arr = []
            for i in range(6):
                index = int(reply_indexes['index'].iloc[i])
                score = float(reply_indexes['score'].iloc[i])
                qns = str(data_language.iloc[:, 0][index])
                ans = str(data_language.iloc[:, 2][index])

                arr.append({
                    "MESSAGE": qns,
                    "RESPONSE": ans,
                    "COS_SIM": score,
                })

            return arr[0]["MESSAGE"], arr[0]["RESPONSE"], arr[1:]

    def Main(self, input):
        if input.lower() != 'bye':
            if self.greeting(input.lower()) is not None:
                return self.greeting(input.lower())
            else:
                reply = self.talk_to_jarvis(str(input), self.data_language, self.model)
                return reply

        else:
            return "Bye!"
