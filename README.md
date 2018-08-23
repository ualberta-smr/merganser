
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

1. **Set the `config.py` file:** The pre-defined paths and database information are stored in  `config.py` file. 
The list of its variables are:

| Variable | Description |
| --- | --- |
| `GITHUB_KEY` | GitHub API key to retrieve the information of repositories
| `REPOSITORY_PATH` | The path to save the cloned repositories
| `TEMP_CSV_PATH` |  The path to save the temporary CSV files before inserting to SQL tables
| `REPOSITORY_LIST_PATH` | The path to save the list of repositories to clone


2. **Add the list of repositories:** The input of the main program is a list of repositories to analyze. There are different waqy to create such list:
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
    
    * **All the repository list manually:** You can simply put the list or repository with `.txt` extension in
     `REPOSITORY_LIST_PATH` directory which is set in `config.py`.
    
