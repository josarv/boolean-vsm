from string import punctuation
from functools import reduce

from decontract import Contractions

from nltk import download, pos_tag
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# decontract and nltk initialization

print("Initializing contractions...")

contractions = Contractions(api_key="glove-twitter-25")
contractions.load_models()

print("Initializing nltk...")

download('punkt_tab')
download('stopwords')
download('wordnet')
download('averaged_perceptron_tagger_eng')

STOPWORDS = set(stopwords.words('english'))
PUNCTUATION = set(punctuation)

def compose(*functions):
    return reduce(lambda f, g: lambda x: g(f(x)), functions, lambda x: x)

def expand_contractions(text):
    return list(contractions.expand_texts([text], precise=True))[0]

def tokenize(text):
    return word_tokenize(text)

def lowercase(tokens):
    return list(map(lambda x: x.lower(), tokens))

def remove_punctuation_tokens(tokens):
    return list(filter(lambda x: x not in PUNCTUATION, tokens))

def remove_digit_tokens(tokens):
    return list(filter(lambda x: not x.isdigit(), tokens))

def remove_stopwords(tokens):
    return list(filter(lambda x: x not in STOPWORDS, tokens))

def remove_too_short_tokens(tokens):
    return list(filter(lambda x: len(x) > 2, tokens))

def add_penn_treebank_tags(tokens):
    pos_tagged_tokens = pos_tag(tokens)
    return pos_tagged_tokens

def map_penn_treebank_to_wordnet_tag(token):
    if token.startswith('J'):
        return wordnet.ADJ
    elif token.startswith('V'):
        return wordnet.VERB
    elif token.startswith('N'):
        return wordnet.NOUN
    elif token.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def convert_penn_treebank_to_wordnet_tags(tokens):
    return list(map(lambda x: (x[0], map_penn_treebank_to_wordnet_tag(x[1])), tokens))

def lemmatize(tokens):
    lemmatizer = WordNetLemmatizer()
    # return list(map(lambda x: lemmatizer.lemmatize(x[0], pos=x[1])), tokens))
    return list(map(lambda x: (lemmatizer.lemmatize(x[0], pos=x[1]), x[1]), tokens))

def get_synonym(word, pos):
    synsets = wordnet.synsets(word, pos=pos)
    if synsets:
        lemma = synsets[0].lemmas()[0].name()
        return lemma.replace('_', ' ')
    return word

def map_to_synonyms(tokens):
    synonym_map = {}
    result = []
    for token in tokens:
        if token not in synonym_map:
            synonym_map[token] = get_synonym(token[0], token[1])
        result.append((synonym_map[token], token[1]))
    return result

def strip_pos_tags(tokens):
    return list(map(lambda x: x[0], tokens))
