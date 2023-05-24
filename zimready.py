from libzim.reader import Archive
from libzim.search import Query, Searcher
from bs4 import BeautifulSoup
from txtai.pipeline import Summary
import time
import sqlite3


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
arts=(list(search.getResults(0, search_count)))

count=0
summary = Summary(gpu=True)

total=search_count
done=0



start = time.time()

print("Beginning summarization... This will take a while...  ")
for i in arts:
    entry = zim.get_entry_by_path(i)
    print(f"Summarizing {entry.title}")
    base_text=(bytes(entry.get_item().content).decode("UTF-8"))

    htmlParse = BeautifulSoup(base_text, 'html.parser')
    base_text=""
    for para in htmlParse.find_all("p"):
        base_text+=(para.get_text())

    text=""
    con=True

    for i in base_text:
        if i=="[":
            con=False
        if con==True:
            text+=i
        if i=="]":
            con=True



    # Create and run pipeline
    #print(summary(text))
    cursor.execute("INSERT INTO summaries VALUES (?, ?)", (entry.title, summary(text)))
    connection.commit()

    count+=1
    progress = (count) / total
    percentage = progress * 100

    print("Articles Summarized:", count, (f", Progress: {percentage:.2f}%"))



end = time.time()
duration = end - start

minutes = int(duration // 60)
seconds = int(duration % 60)

print(f"All articles were summarized in {minutes} minutes and {seconds} seconds.")
