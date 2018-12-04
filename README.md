
# Merganser

 [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) 
 [![Build Status](https://travis-ci.com/ualberta-smr/merganser.svg?token=hjqcPpPsw5pg2YPrs9sB&branch=master)](https://travis-ci.com/ualberta-smr/Merge-Excavator)

This repository provides a toolchain for gathering and analyzing merge scenarios found in git repositories and store them in a normalized MySQL database It supports extracting various features of the merge scenario as well as executing the merge using different merge tools. It also supports compiling and testing the resulting resolutions. Currently, only _Maven_ is supported.

_The tool chain has been tested with Ubuntu 18.04._

# Setup
1. Clone this repository:

```bash
git https://github.com/ualberta-smr/code-owhadi-msr19.git
```


2. Install required tools and packages using this script (Note that this requires sudo priveleges. 
Check the list before executing this script and adapt according to your needs to avoid breaking your packages)

```bash
sudo ./setup.py
``` 

# Usage 

1. **Set the `config.py` file:** The pre-defined paths, database information, constants, and access keys are stored in  `config.py` file. The full dewcription of these parameters are in [the wiki page](https://github.com/ualberta-smr/merganser/wiki/Parameters-in-config.py). The only parameters that the user must set before using Merganser are the HitHub access keys and database parameters.
The list of its variables are:

2. **Add the list of repositories:** The input of the main program is a list of repositories to analyze. There are different waqy to create such list:

    * **All the repository list manually:** You can simply put the list or repository with `.txt` extension in
     `REPOSITORY_LIST_PATH` directory which is set in `config.py`.

    * **Automatic searching:** You can search the list of repositories by:
    
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

3. **Run the main script:** To run the tool, you can run this command:

```bash
python3 main.py <parameters>  
```    
Here are the list of parameters:

| Parameter | Description |
| --- | --- |
| `-r` or `--repository-list` | The list of GitHub repositories |
| `-c` or `--compile` | If set, the merged code (if successfully merged using the given tool) will be compiled |
| `-t` or `--test` | If set, the repository\'s test suite will be run after a successful merge |   
| `-cf` or `--conflicting-file` | If set, the `Conflicting_File` table will be populated |
| `-cr` or `--conflicting-region` | If set, the `Conflicting_Region` table will be populated |
| `-pr` or `--pull-request` | If set, pull requests are detected |
| `-rc` or `--replay-compare` | If set, the replays and merge commits are compared |
| `-cd` or `--commit-details` | If set, the information of all commits that are involved in merge scenarios are extracted |
| `-sv` or `--style-violation` | If set, the code style violations are extracted |
| `-cc` or `--code-complexity` | If set, the code complexity are extracted |
| `-cores` or `--cpu-cores` | The number of threads. The default value is ALL logical cores on the system. |

To run the toolchain with all features, you can simply run `./runAll <repository_list>`. For example, to run the toolchain
on _spark_ repository, run `./runAll spark`.

