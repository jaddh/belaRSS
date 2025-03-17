from reader import make_reader

reader = make_reader('db.sqlite')

# add feed to the reader
#reader.add_feed('http://localhost:1200/telegram/channel/hibrpresse')
reader.add_feed('http://localhost:1200/twitter/user/aljumhuriya_net')

# remove feed from the reader
#reader.delete_feed('https://www.kurdistan24.net/en/rss')


print("reader connected")

