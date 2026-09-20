FROM python:3.12-slim

WORKDIR /ir

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# bake the nltk corpora into the image so the container runs offline
RUN python -m nltk.downloader -d /usr/share/nltk_data \
    punkt_tab stopwords wordnet averaged_perceptron_tagger_eng
ENV NLTK_DATA=/usr/share/nltk_data

COPY . .

CMD ["python", "-m", "project.driver"]
