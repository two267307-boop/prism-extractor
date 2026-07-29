# prism-extractor

A simple and easy-to-use Python tool for extracting information about YouTube channels.

## Overview

**prism-extractor** Is a tool for extracting info for YouTube channels, built on python.

The goal of this project is to simplify YouTube analyzation, making it easier to gain a good sight of things.

## Installation
Clone the repository:

```
git clone https://github.com/two267306-boop/prism-extractor.git
```
Navigate into the project folder:

    cd prism
To install the required dependencies, run:

```bash
pip install -r requirements.txt
```
or download the py file*s manually from the repository.
## Usage

Start the program by running:

```
python prism.py --channel -timeout (1 by default)
```

To reuse existing data use ``--reuse`` or ``-r`` only.
By default, the timeout is set to one, meaning it will wait two seconds before starting another video. This may cause YouTube to rate limit you. In case an error occurs, by default the program will wait 60 seconds before starting of again.

Use ``--save`` or ``-s`` to automatically save the plot as a picture. You can still export it even with having this disabled.
## Features

- Simple information extraction
- Graph with all information
- Automatically saves to csv file

## Requirements

- Python 3
- Dependencies listed in `requirements.txt`

Partially made with AI. Mainly used to get the basics, I expanded on them further myself.