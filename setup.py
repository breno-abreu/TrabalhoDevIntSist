import os, sys, pathlib
from config import db

newpath = str(pathlib.Path(__file__).parent.resolve())
newpath = newpath.replace("\\","/")
newpath = newpath +  '/data'

print(newpath)
if not os.path.exists(newpath):
    print("Folder created at: " + newpath)
    os.makedirs(newpath)

db.create_all()