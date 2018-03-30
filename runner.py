import os
os.chdir('functions/write')

from functions.write import main
print('result=', main.handle(1,2))
