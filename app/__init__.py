from flask import Flask

import nltk
nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)

from app.controllers import default
from app.controllers import info
from app.controllers import new_author
from app.controllers import resume
from app.controllers import word_operation