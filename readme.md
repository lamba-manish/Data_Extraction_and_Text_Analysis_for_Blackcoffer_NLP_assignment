## Dependencies

The code requires the following dependencies. You can install them using `pip` or any other Python package manager.

- pandas==1.3.0
- nltk==3.6.3
- beautifulsoup4==4.9.3
- requests==2.26.0

## Usage

1. Make sure you have the required dependencies installed. You can use the provided `requirements.txt` file to install them by running the following command: 'pip install -r requirements.txt'

2. Create the necessary directories: `text_files`, `StopWords`, and `MasterDictionary`. Populate the directories with the required files.

3. Open terminal inside current directory (dsa_test_assignment) and Run the code by executing the `main.py` file: 'python main.py'


This will initiate the data processing tasks and generate the output file `output.csv` containing the processed data.

## Directory Structure

The directory structure of the project is as follows:
    ├── main.py
    ├── text_files/
    ├── StopWords/
    ├── MasterDictionary/
    ├── Input.xlsx
    ├── output.csv
    ├── requirements.txt
    └── README.md


- `main.py`: The main script to initiate the data processing.
- `text_files/`: Directory to store text files extracted from URLs.
- `StopWords/`: Directory to store stop words files.
- `MasterDictionary/`: Directory to store the master dictionary files containing positive and negative words text files
- `Input.xlsx`: Input data file containing URLs and other information.
- `output.csv`: Output data file containing the processed data.
- `requirements.txt`: File specifying the required dependencies.
- `README.md`: This file, providing an overview of the project.
- `blackc0ffer_logs.log`: This file will contain the logs of module

** Please copy main.py file inside the test assignment folder where StopWords folder with stop words file, MasterDictionary file with positive and negative words file, and Input.xlsx files are already present, if not please provide the path for them inside the main.py python script**

** If you have text file already present inside the 'text_files' folder with name as 'URL_ID.txt' for each URL in 'Input.xlsx', or you want to run again this script and want to skip the fetching of data again, you can comment the line no 29: 'self.extract_and_save_text_data()' inside the 'process_data' method in main.py python script**

## Thanks and Regards
## Manish Lamba
## manishlamba002@gmail.com
## 8092249902