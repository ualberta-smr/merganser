
# Merganser

 [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) 
 [![Build Status](https://travis-ci.com/ualberta-smr/merganser.svg?token=hjqcPpPsw5pg2YPrs9sB&branch=master)](https://travis-ci.com/ualberta-smr/merganser)

This repository provides a toolchain for gathering and analyzing merge scenarios found in git repositories. The tool stores the collected data in a normalized MySQL database. It supports extracting various features of the merge scenarios as well as executing the merge using different merge tools, detecting merge conflicts, and finding compilation and test problems with the merge resolution.

_The toolchain has been tested with Ubuntu 20.04._

## Setup
1. Clone this repository:
```bash
git https://github.com/ualberta-smr/merganser
```

2. Install the dependencies.
```bash
pip3 install -r requirements.txt
``` 

## Usage 

1. **Set the `config.py` file:** The pre-defined paths, database information, constants, and access keys are stored in  `config.py` file. The full description of these parameters is in [the wiki page](https://github.com/ualberta-smr/merganser/wiki/Parameters-in-config.py). The only parameters that the user must set before using Merganser are the GitHub access keys and database parameters.

2. **Add the list of repositories:** The input of the main program is a list of repositories to analyze. There are different ways to create such list:

    * **Add the repository list manually:** If you already have the list of repositories to analyze, write them in a *\*.txt* file (each repository per line) and copy the text file in `./working_dir/repository_list` (this path is `REPOSITORY_LIST_PATH`  which is set in `config.py`).

    * **Automatic searching:** If you do not have specific repositories in mind, but instead, want to analyze repositories with a specific range of stars, watches, forks, size, or that are in a specific application domain, you can search the list of repositories using `search_repository.py`. Read [the wiki page](https://github.com/ualberta-smr/merganser/wiki/Search-for-Repositories) to find out the parameters of this module.

3. There are two ways to run the tool based on the final goal. the results are stores in CSV files.
    * Execute the  tool to extract all available data:

    ```bash
    python3 ./run_predict.sh <list_of_repositories>
    ```
    * Execute the tool for conflict prediction data:
    
    ```bash
    python3 ./run_all.sh <list_of_repositories>
    ```
        
4. The next step is storing the the CSV files in a SQL database.

```bash
python3 ./data_conversion.py
```

5. For conflict prediction, first create the data:

```bash
python3 ./data_prediction.py
```

### Conflict Prediction


[The wiki page](https://github.com/ualberta-smr/merganser/wiki/Running-the-Merganser) describes all possible parameters.

## License
Merganser is released under the [MIT License](https://choosealicense.com/licenses/mit/).

## Support
Feel free to report any issue about Merganser [here](https://github.com/ualberta-smr/merganser/issues). You can ask your question about installing and running the tool from the creators [Moein Owhadi Kareshk](https://github.com/owhadi) and [Sarah Nadi](https://sarahnadi.org/).

## Contribution
You are very welcome to [post a pull-request](https://github.com/ualberta-smr/merganser/pulls) should you have change, bug fix,  etc. in mind. 

