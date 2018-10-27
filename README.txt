1. Run chatbot.py to start UI.
2. Go to any web browser and type http://localhost:8000/

File Description:
 - Code
  - chatbot.py = Run this .py file to start UI.
  - StackOverflow_Word2Vec.py = Chatbot backend.

Python Library Required:
from flask import Flask, render_template
from flask import request, Response
from json import dumps
import pandas as pd
import json
import re
import random
import nltk
from nltk.corpus import stopwords
import gensim
from sklearn.metrics.pairwise import cosine_similarity