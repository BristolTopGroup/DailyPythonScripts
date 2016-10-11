import os

dir = 'dummy/res/'

files = os.listdir(dir)

for file in files:
    if file.find('.tar') >= 0:
        command='tar -xf '+dir+'/'+file+' -C '+dir
#         print command
        os.system(command)
        pass
    pass
