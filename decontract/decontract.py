from .contractions import simple_contractions, contextual_contractions, expansions

import gensim.downloader as api
from gensim.models import KeyedVectors
from itertools import combinations_with_replacement, permutations
import language_tool_python
import os


class Contractions(object):
    """Expand and contract common English contractions in text.

    Uses a combination of pattern replacement, grammar checking, and Word Mover's Distance.
    """

    def __init__(self, w2v_path=None, lang_code='en-US', kv_model=None, api_key=None):
        """w2v_path is a path to an embedding model used for calculating the Word Mover's Distance."""
        self.w2v_path = w2v_path
        self.lang_code = lang_code
        self.kv_model = kv_model
        self.api_key = api_key
        self.lc_tool = None

    def load_models(self):
        """Attempt to find/load/download keyedvector model."""
        if self.kv_model is not None:
            if not hasattr(self.kv_model, 'wmdistance'):
                raise AttributeError("Model does not support Word Mover's Distance, must be in keyedvectors format")

        elif self.w2v_path is not None:
            if not os.path.exists(self.w2v_path):
                raise AttributeError("Word2Vec model not found at {}".format(self.w2v_path))
            try:
                self.kv_model = KeyedVectors.load_word2vec_format(self.w2v_path, binary=True)
            except:
                print("Error loading Word2Vec model")
                raise
        elif self.api_key is not None:
            try:
                self.kv_model = api.load(self.api_key)
            except:
                print("Error downloading model {}".format(self.api_key))
                raise
            if not hasattr(self.kv_model, 'wmdistance'):
                raise AttributeError("Model does not support Word Mover's Distance, must be in keyedvectors format")
        else:
            raise AttributeError("No model given")

        try:
            self.lc_tool = language_tool_python.LanguageTool(self.lang_code)
        except:
            print("Error initializing LanguageTool")
            raise

    def _expand_text(self, text, scores=False):
        """Expand contractions in text using a faster but imprecise method."""
        intermediates = []
        for pattern, rep in simple_contractions.items():
            text = pattern.sub(rep, text)
        for pattern, options in contextual_contractions.items():
            if pattern.search(text):
                hyp = []
                for opt in options:
                    # Assumes all uses of the pattern are the same in one text which doesn't always hold
                    text1 = pattern.sub(opt, text)
                    hyp.append((text1, self.kv_model.wmdistance(
                        text.split(), text1.split()), len(self.lc_tool.check(text1))))
                hyp = sorted(hyp, key=lambda x: (x[2], x[1]))
                # The text of the first item is most likely correct
                text = hyp[0][0]
                if scores:
                    intermediates.append(hyp)
        return (text, intermediates)

    def _expand_text_precise(self, text, scores=False):
        """Expand contractions in text using a much slower but more precise method."""
        intermediates = []
        for pattern, rep in simple_contractions.items():
            text = pattern.sub(rep, text)
        for pattern, options in contextual_contractions.items():
            num_matches = len(pattern.findall(text))
            if num_matches > 0:
                hyp = []
                # If n = len(options) and m = num_matches:
                # This performs (n+m-1)! / m! / (n-1)! total iterations
                for perm_set in (set(permutations(comb)) for comb in combinations_with_replacement(options,
                                                                                                   num_matches)):
                    # This performs sum(n * m! / (m-x)! * (x+1) for x in range(m)) total iterations
                    for perm in perm_set:
                        text1 = text
                        # This performs sum(n * m! / (m-x)! * (x+1) for x in range(m)) * m total iterations
                        for opt in perm:
                            text1 = pattern.sub(opt, text1, count=1)
                        hyp.append((text1, self.kv_model.wmdistance(
                                    text.split(), text1.split()), len(self.lc_tool.check(text1))))
                hyp = sorted(hyp, key=lambda x: (x[2], x[1]))
                # The text of the first item is most likely correct
                text = hyp[0][0]
                if scores:
                    intermediates.append(hyp)
        return (text, intermediates)

    def expand_texts(self, texts, precise=False, scores=False):
        """Return a generator over an iterable of text where each result has common contractions expanded.

        If precise == True then it will use a much slower method that does not assume all occurrences
        of the same contraction in the text have the same expansion.  If scores == True, it will return
        a generator over a list of lists of intermediate results with their scores and number of grammar errors.
        """
        if self.lc_tool is None:
            self.load_models()

        if precise:
            _fn = self._expand_text_precise
        else:
            _fn = self._expand_text

        for text in texts:
            text, intermediates = _fn(text, scores)
            if scores:
                yield intermediates
            else:
                yield text

    def contract_texts(self, texts):
        """Return a generator over an iterable of text where each result has contracted common expansions."""
        for text in texts:
            for pattern, rep in expansions.items():
                text = pattern.sub(rep, text)
            yield text
