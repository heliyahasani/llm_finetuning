import pandas as pd
import os
import toml
import PyPDF2



from datasets import Dataset

class loaded_data:
    def __init__(self,file_name):
        self.file_name = file_name
    def file_extension(self):
        return self.file_name.split('.')[-1]
        
    def load_file_to_dataframe(filepath):
        # Determine the file type from the extension
        file_extension = self.file_extension()
        # Read the file based on its file type
        if file_extension == '.csv':
            dataframe = pd.read_csv(filepath)
        elif file_extension == '.parquet':
            dataframe = pd.read_parquet(filepath)
        elif file_extension in ['.txt', '.log']:
            dataframe = pd.read_csv(filepath, header=None, names=['data'])
        elif file_extension in ['.xlsx', '.xls']:
            dataframe = pd.read_excel(filepath)
        elif file_extension == '.json':
            dataframe = pd.read_json(filepath)
        elif file_extension == '.pdf':
            with open(filepath, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfFileReader(pdf_file)
                # Initialize an empty list to store text data
                pdf_text_data = []
                # Loop through each page and extract text
                for page_num in range(pdf_reader.numPages):
                    page = pdf_reader.getPage(page_num
    



