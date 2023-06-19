import pyan
from IPython.display import HTML

HTML(pyan.create_callgraph(filenames="test/callgraph_.py", format='html'))