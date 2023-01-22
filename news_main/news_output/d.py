from elasticsearch_dsl import Q
from news_main.news_output.documents import NewsDocument


# Выполняет поиск всех статей, в названии которых есть «How to».
query = 'How to'
q = Q(
     'multi_match',
     query=query,
     fields=[
         'title'
     ])
search = NewsDocument.search().query(q)
response = search.execute()

# распечатать все хиты
for hit in search:
    print(hit.title)