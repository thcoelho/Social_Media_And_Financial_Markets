import twint as tw
import nest_asyncio
nest_asyncio.apply()

c = tw.Config()
c.Search = "Bitcoin"
c.Limit = 10
c.Pandas = True

tw.run.Search(c)
