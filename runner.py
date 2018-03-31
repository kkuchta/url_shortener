import os
os.chdir('functions/index')

from functions.index import main
print('result=', main.handle(1,2))
