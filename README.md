I'll fill this in later.

Currently no way to install this module, so unless you want to add the directory
to your PYTHONPATH, you need to play from the directory *above* `__init__.py`
by opening a python terminal and typing:

```python
import taah
taah.play()
```

To download wiktionary data for offline play (now the default), first run the code below (it takes a while):

```python
from taah import data
data.download_raw()
data.process_raw()
```

Also pip install the packages you don't have. And this only works with Python3.

Good luck!
