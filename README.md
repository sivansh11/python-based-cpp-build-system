# python-based-cpp-build-system
this is an old project I made and used before learning how cmake works


#How to use
At the top of the compile.py file, add the library folder path to paths_to_search variable, add any include folder to include variable, and any library to the link_libs variable

NOTE: make sure that any external library that you may wanna add is in this particular folder structure

external:
  lib1:
    src:
    include:
  lib2:
    src:
    include:
    
 src:
 
 include:
    
the main porject's src can just be added just like that, you can also make sub directories in the directories that is been added to the search and it will recursivly get the folder's contents
