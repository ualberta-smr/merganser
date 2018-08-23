
# Merge Excavator

This repository provides a tool chain for gathering and analyzing merge scenarios found in git repositories. 
It supports extracting various features of the merge scenario as well as executing the merge using different merge tools.
It also supports compiling and testing the resulting resolutions. Currently, only _Maven_ is supported.

The tool chain has been tested with Ubuntu 18.04. 

# Setup
1. Clone this repository:

```bash
git https://github.com/ualberta-smr/code-owhadi-msr19.git
```

2. Install required tools and packages using this script (Note that this requires sudo priveleges. 
Check the list before executing this script and adapt according to your needs to avoid changing versions of the
 tools you may already have)

```bash
./setup.py
``` 

# Usage 

1. The input of the main program is a list of repositories to analyze. There are different waqy to create such list:
    * **Automatic searching:** THe list of GitHub repositories is searched by:
    
    ```bash
    python3 search_repository.py
    ```
    Here are the list of mandotary parameters:
    
    | Parameter | Description |
    | --- | --- |
    | `-q` or `--query` | The query of searching |
    | `-s` or `--star` | The minimum number of stars |
    | `-f` or `--fork` | The minimum number of forks |
    | `-l` or `--language` | The language of repositories | 
    | `-o` or `--output` | The name of the output file |  
    
    As an example, to store the list of data related repositories in Python with more than 200 stars and 100 fork in
     `data_popular_python_repos.txt` file, you should execute:
     
    ```bash
    python3 search_repository.py -q data -s 200 -f 100 -l python -o data_popular_python_repos
    ```  
    
    
    
    
    
    
    
    
    
    

1. First, you need to create a list of repositories in `reposList` _directory_. The name of the file should be <FILE_NAME>list.txt. There are multiple sample lists already included in the directory.
2. After that, you can run the code by running `main.py`. For example, if you want to analyze the merge scenarios in the sample list repositories (listed in `sampleList.txt` under `reposList` directory), using Git merge, the running script is:

```
sudo python3 main.py -r sample -m uns
```

The script supports various options as follows:
```
usage: main.py [-h] -r REPOSITORY_LIST -m MERGE_METHOD [-c COMPILE] [-t TEST]
               [-fc FILE_COMPILE] [-s SEMANTIC_CHANGES]

The main script for analyzing merge scenarios

optional arguments:
  -h, --help            show this help message and exit
  -r REPOSITORY_LIST, --repository-list REPOSITORY_LIST
                        The list of GitHub repositories
  -m MERGE_METHOD, --merge-method MERGE_METHOD
                        The merge method ("uns", "strc", "at", and "semiStrc"
                        for unstructured, structured, auto-tuning, and semi-
                        structured, respectively)
  -c COMPILE, --compile COMPILE
                        If set, the merged code (if successfully merged using
                        the given tool) will be compiled afterwards
  -t TEST, --test TEST  If set, the repository's test suite will be run after
                        a successful merge
  -fc FILE_COMPILE, --file-compile FILE_COMPILE
                        This flag determines whether the repositories should be
                        compiled only on the file level
  -s SEMANTIC_CHANGES, --semantic-changes SEMANTIC_CHANGES
                        This flag determines whether the semantic changes
                        should be extracted

```

3. [Here](https://github.com/ualberta-smr/code-owhadi-merge/tree/master/datamodel/model.png) is the data schema:


To convert the data, simply run the following script:
```
sudo python3 data2SQL.py
```
It asks one time for sudo password and 4 times for the MySQL password, and the default username is _root_. The data is stored in the _mydb_ schema.





