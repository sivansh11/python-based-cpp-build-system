from fileinput import filename
import os
import hashlib
from colorama import Fore


include_folder = 'include'
src_folder = 'src'
# GL_folder = 'libs/glad'
# imgui_folder = 'libs/imgui' 
# stb_folder = 'libs/stb_image'
# tiny_obj_loader_folder = 'libs/tinyObjLoader'
# glm_folder = 'libs/glm'
# json_folder = 'libs/json'

paths_to_search = [include_folder, src_folder]  #, GL_folder, imgui_folder, stb_folder, tiny_obj_loader_folder, glm_folder, json_folder]

saved = 'pystuff/filehash.txt'

o_folder = 'build'

app_name = 'app'

flags = ['-std=c++17', '-g', '-D DEBUG']
# flags = ['-std=c++17', '-g']
includes = ['-I include/']  #, '-I libs/imgui/include/', '-I libs/stb_image/include/', '-I libs/glad/include/', '-I libs/tinyObjLoader/include', '-I libs/json/include']
link_libs = []  #'-lglfw', '-lGL', '-ldl']


def read_file(file_path):  # Reads all lines in a file and stores them in a list (line by line)
    file = open(file_path, 'r')
    lines = file.readlines()
    file.close()
    return lines


def get_file_hash_from_file(file_path):  # reads the saved file parses it (ie split the filepath and respective hash)
    lines = read_file(file_path)
    file_hash = dict()
    for line in lines:
        name, hash = line.split(' ')
        hash = hash.replace('\n', '')
        file_hash[name] = hash
    return file_hash


def get_all_files(path_to_search):  # takes in a folder path and returns all files that the folder can touch (even files in side the folder in side the folder)
    files = list()
    for path in os.listdir(path_to_search):
        if not os.path.isdir(path_to_search + '/' + path):
            files.append(path_to_search + '/' + path)
        else:
            deeper_files = get_all_files(path_to_search + '/' + path)
            for file in deeper_files:
                files.append(file)
    return files
    

def get_file_hash_from_paths(paths_to_search):  # searches for files in a directory and stores all the respective hashes in a dictionary for fast lookups
    file_hash = dict()
    files_to_check = list()
    for path in paths_to_search:
        if os.path.isdir(path):
            for file in get_all_files(path):
                files_to_check.append(file)            
        else:
            print(f'path given is not a valid path\n\t\tpath specified: {path}')
            quit(1)
    for file_path in files_to_check:
        file_hash[file_path] = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
    return file_hash


def save_file_hash(file_hash, path):  # converts the dictionary to file with format filename hash
    lines = list()
    for file_path in file_hash.keys():
        lines.append(file_path + ' ' + file_hash[file_path] + '\n')
    file = open(path, 'w')
    file.writelines(lines)
    file.close()


def get_dependencies_of_file(path_to_file):  # parses the file and returns all the files it depends on
    file = open(path_to_file, 'r')
    lines = file.readlines()
    dependencies = list()
    for line in lines:
        if "#include " in line:
            new_line = line.replace('\n', '')
            new_line = new_line.replace('#include ', '')
            new_line = new_line.replace('"', '')
            new_line = new_line.replace('<', '')
            new_line = new_line.replace('>', '')
            dependencies.append(new_line)
    file.close()
    return dependencies


def get_dependency_of_files_from_path(paths_to_search):
    filepath_dependency = dict()
    for path in paths_to_search:
        if os.path.isdir(path):
            for file in get_all_files(path):
                dependencies = get_dependencies_of_file(file)
                for dep_file in dependencies:
                    if dep_file not in filepath_dependency:
                        filepath_dependency[dep_file] = set([file])
                    else:
                        filepath_dependency[dep_file].add(file)
        else:
            print(f'path given is not a valid path\n\t\tpath given: {path}')
            quit(1)

    return filepath_dependency


def ret(lis):
    strr = ''
    for i, v in enumerate(lis):
        strr += v
        if i < len(lis) - 1:
            strr += ' '
    return strr 


class Builder:
    def __init__(self, paths_to_search, file_path) -> None:
        self.new_file_hash = get_file_hash_from_paths(paths_to_search)
        self.old_file_hash = get_file_hash_from_file(file_path)

    def get_changed_list(self):
        changed_list = list()
        for file_path in self.new_file_hash.keys():
            if file_path in self.old_file_hash:
                if self.new_file_hash[file_path] != self.old_file_hash[file_path]:
                    changed_list.append(file_path)
            else:
                changed_list.append(file_path)
        return changed_list
    
    def save(self, file_name):
        save_file_hash(self.new_file_hash, file_name)


def compile(changes):
    for file_path in changes:  # compile individual files
        if 'src/' in file_path:
            if '.cpp' in file_path:
                file = file_path.replace('.cpp', '')
            else:
                file = file_path.replace('.c', '')
            file = file.replace('src/', '')
            if 'libs/' in file_path:
                file = file.replace('libs/', '')
                folder, file = file.split('/')
            if '/' in file_path:
                file = file.split('/')
                file = file[-1]
            cmd = f'g++ {ret(flags)} {ret(includes)} -c ' + file_path + f' -o {o_folder}/' + file + '.o'
            print(Fore.LIGHTBLUE_EX + cmd + Fore.WHITE)
            if os.system(cmd) != 0:
                quit(1)        


def link():  # linking
    o_files = os.listdir(o_folder)
    cmd = f'g++ {ret(flags)} {ret(includes)} -o bin/{app_name} '
    for file in o_files:
        cmd += f'{o_folder}/' + file + ' '
    cmd += ret(link_libs) 
    print(Fore.YELLOW + cmd + Fore.WHITE)
    if os.system(cmd) != 0:
        quit(1)

def run():
    if not os.path.isdir('pystuff'):
        os.system('mkdir pystuff')
    if not os.path.isfile('pystuff/filehash.txt'):
        os.system('>pystuff/filehash.txt')
    if not os.path.isdir('bin'):
        os.system('mkdir bin')
    if not os.path.isdir('build'):
        os.system('mkdir build')
    if not os.path.isdir('include'):
        os.system('mkdir include')
    if not os.path.isdir('src'):
        os.system('mkdir src')
    hashfile = Builder(paths_to_search, saved)
    changes = hashfile.get_changed_list()
    print(Fore.GREEN + 'created changes list!' + Fore.WHITE)
    dependencies = get_dependency_of_files_from_path(paths_to_search)
    print(Fore.GREEN + 'created dependency list!' + Fore.WHITE)

    for i in range(5):
        for changed_file in reversed(changes):
            names = changed_file.split('/')
            file_name = ''
            for i in range(1, len(names)):
                name = names[i]
                file_name += name
                file_name += '/'
            file_name = file_name[:-1]
            if file_name in dependencies:
                for dep_file in dependencies[file_name]:
                    if dep_file not in changes:
                        changes.append(dep_file)

    compile(changes)
    hashfile.save(saved)
    if not changes:
        print(Fore.CYAN + "no files to be recompiled!" + Fore.WHITE)
    if changes or not os.path.isfile('bin/' + app_name):
        link()
        print(Fore.CYAN + "Done!" + Fore.WHITE)

        
run()

    
