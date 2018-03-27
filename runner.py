import os
os.chdir('functions/iterator')

from functions.iterator import main
print('result=', main.handle(1,2))
