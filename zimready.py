from libzim.reader import Archive
from libzim.search import Query, Searcher
from bs4 import BeautifulSoup
import time
import sqlite3
import re

from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

def summarize(text):
    sentences = sent_tokenize(text)
    vectorizer = TfidfVectorizer()
    sentence_vectors = vectorizer.fit_transform(sentences)
    representative_sentence_idx = sentence_vectors.sum(axis=1).argmax()
    summary = sentences[representative_sentence_idx]
    return summary

connection = sqlite3.connect("wikipedia.db")
cursor = connection.cursor()

zim = Archive("wikipedia_en_100_2023-04.zim")
print(f"Main entry is at {zim.main_entry.get_item().path}")

# searching using full-text index
search_string = "a"
query = Query().set_query(search_string)
searcher = Searcher(zim)
search = searcher.search(query)
search_count = search.getEstimatedMatches()
print(f"There are {search_count} matches for {search_string}")
arts = search.getResults(0, search_count)

count = 0
total = search_count
done = 0

start = time.time()

print("Beginning summarization... This will take a while...  ")
for i in arts:
    entry = zim.get_entry_by_path(i)
    print(f"Summarizing {entry.title}")
    base_text = bytes(entry.get_item().content)
    html_parse = BeautifulSoup(base_text, 'html.parser')
    paragraphs = html_parse.find_all("p")
    base_text = " ".join([para.get_text() for para in paragraphs])
    base_text = re.sub(r'\[.*?\]', '', base_text)
    text = summarize(base_text)
    cursor.execute("INSERT INTO summaries VALUES (?, ?)", (entry.title, text))
    connection.commit()
    count += 1
    progress = count / total
    percentage = progress * 100
    print("Articles Summarized:", count, (f", Progress: {percentage:.2f}%"))

end = time.time()
duration = end - start

minutes = int(duration // 60)
seconds = int(duration % 60)

print(f"All articles were summarized in {minutes} minutes and {seconds} seconds.")
