
# Merganser

 [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) 
 [![Build Status](https://travis-ci.com/ualberta-smr/merganser.svg?token=hjqcPpPsw5pg2YPrs9sB&branch=master)](https://travis-ci.com/ualberta-smr/merganser)
 ![GitHub repo size in bytes](https://img.shields.io/github/size/ualberta-smr/merganser/build/phaser-craft.min.js.svg)

This repository provides a toolchain for gathering and analyzing merge scenarios found in git repositories and store them in a normalized MySQL database It supports extracting various features of the merge scenario as well as executing the merge using different merge tools, detects merge conflicts, and find the compilation and test problems.

_The toolchain has been tested with Ubuntu 18.04._

## Setup
1. Clone this repository:
```bash
git https://github.com/ualberta-smr/code-owhadi-msr19.git
```

2. Install required tools and packages using this script (Note that this requires sudo privilege. 
Check the list before executing this script and adapt according to your needs to avoid breaking your packages)
```bash
sudo ./setup.py
``` 

## Usage 

1. **Set the `config.py` file:** The pre-defined paths, database information, constants, and access keys are stored in  `config.py` file. The full description of these parameters is in [the wiki page](https://github.com/ualberta-smr/merganser/wiki/Parameters-in-config.py). The only parameters that the user must set before using Merganser are the GitHub access keys and database parameters.

2. **Add the list of repositories:** The input of the main program is a list of repositories to analyze. There are different ways to create such list:

    * **Add the repository list manually:** If you already have the list of repositories to analyze, write them in a *\*.txt* file (each repository per line) and copy the text file in `./working_dir/repository_list` (this path is `REPOSITORY_LIST_PATH`  which is set in `config.py`).

    * **Automatic searching:** If you do not have specific repositories in mind, but instead, want to analyze the repositories with the specific range of stars, watches, forks, size, or are in a specific application domain, you can search the list of repositories by `search_repository.py`. Read [the wiki page](https://github.com/ualberta-smr/merganser/wiki/Search-for-Repositories) to find out the parameters of this module.

3. **Run the main script:** To run the tool, you can run this command:

```bash
python3 main.py <parameters> 
```

[The wiki page](https://github.com/ualberta-smr/merganser/wiki/Running-the-Merganser) describe all possible parameters.

## License
Merganser is release under [MIT License](https://choosealicense.com/licenses/mit/).

## Support
Feel free to report any issue about Merganser [here](https://github.com/ualberta-smr/merganser/issues). You can ask your question about installing and running the tool from the creators [Moein Owhadi Kareshk](https://github.com/owhadi) and [Sarah Nadi](https://sarahnadi.org/).

## Contribution
You are very welcome to [post a pull-request](https://github.com/ualberta-smr/merganser/pulls) should you have change, bug fix,  etc. in mind. 

## Disclaimer
While the users are free to use Merganser for both commercial and academic purposes, you should use this tool on your risk. Although we tried our best to release an effective tool, the creators are not responsible for any software/hardware problems caused by using Merganser, or inconsistencies in the results. 
