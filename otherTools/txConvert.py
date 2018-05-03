import os
#from tqdm import tqdm

convertDir=raw_input("Directory to Convert: ")
#convertDir="/users/admin/hale38/PycharmProjects/txTiff/testTx"



def walkDir(dir,newDir):

    print "Starting Conversion"
    for file in os.listdir(dir):
        if file.find('tex'):
            newName= file.split('.')[0]+'.tiff'
            command = "txmake "+dir+'/'+file+' '+newDir+'/'+newName
            #print command
            os.system(command)
    print "Done! Enjoy your tiffs"

if os.path.isdir(convertDir):
    newDirname=convertDir.split('/')[-1]
    newDir=newDirname+'_tiffs'
    newDirpath=convertDir.replace(newDirname,newDir)

    if not os.path.isdir(newDirpath):
        os.system("mkdir " + newDirpath)



    walkDir(convertDir,newDirpath)

else:
    print "Not a valid directory"

