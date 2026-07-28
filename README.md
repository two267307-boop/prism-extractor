# prism-extractor

A simple and easy-to-use Python tool for extracting information about YouTube channels.

## Overview

**prism-extractor** is a lightweight analysis program built with Python that allows users to gather and analyze information from YouTube content.

The goal of this project is to simplify YouTube analyzation, making it easier to gain a good sight of things.

## Installation
Clone the repository:

```
git clone https://github.com/two267306-boop/prism-extractor.git
```
Navigate into the project folder:

    cd prism-extractor
To install the required dependencies, run:

```bash
pip install -r requirements.txt
```
## Usage

Start the program by running:

```
python prism.py --channel -timeout (1 by default)
```

To reuse existing data use ```--reuse``` only.
By default, the timeout is set to one, meaning it will wait two seconds before starting another video. This may cause YouTube to rate limit you. In case an error occurs, by default the program will wait 60 seconds before starting of again.

## Features

- Simple information extraction
- Graph with all information
- Automatically saves to csv file.

## Requirements

- Python 3
- Dependencies listed in `requirements.txt`

