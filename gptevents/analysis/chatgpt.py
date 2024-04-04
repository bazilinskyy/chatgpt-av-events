# by Pavlo Bazilinskyy <pavlo.bazilinskyy@gmail.com>
import os
import pandas as pd
from tqdm import tqdm
import openai


import gptevents as gpte

# warning about partial assignment
pd.options.mode.chained_assignment = None  # default='warn'

logger = gpte.CustomLogger(__name__)  # use custom logger


class ChatGPT:
    # pandas dataframe with extracted data
    data = pd.DataFrame()
    save_p = False  # save data as pickle file
    load_p = False  # load data as pickle file
    save_csv = False  # save data as csv file
    # pickle file for saving data
    file_p = 'data.p'
    # csv file for saving data
    file_data_csv = 'data.csv'

    def __init__(self,
                 files_reports: list,
                 save_p: bool,
                 load_p: bool,
                 save_csv: bool):
        # list of files with raw data
        self.files_reports = files_reports
        # save data as pickle file
        self.save_p = save_p
        # load data as pickle file
        self.load_p = load_p
        # save data as csv file
        self.save_csv = save_csv
        # client for communicating with GPT4-V
        self.gpt_client = openai.OpenAI(api_key=gpte.common.get_secrets('openai_api_key'))

    def read_data(self, filter_data=True, clean_data=True, analyse_data=True):
        """Read data into an attribute.

        Args:
            filter_data (bool, optional): flag for filtering data.
            clean_data (bool, optional): clean data.
            analyse_data (bool, optional): analyse data.

        Returns:
            dataframe: updated dataframe.
        """
        # load data
        if self.load_p:
            df = gpte.common.load_from_p(self.file_p, 'chatgpt data')
        # get data based on the reports
        else:
            # pandas df to store data
            df = pd.DataFrame(columns=('report', 'response'))
            # df = df.transpose()
            # go over all reports
            for file in tqdm(os.listdir(self.files_reports)):
                logger.info('Processing report {}.', file)
                # get pages as base64_image strings
                pages = self.pdf_to_base64_image(file)
                # feed all pages in the report to GPT-4V at once
                df = pd.concat([df, self.ask_gptv(file, pages)], ignore_index=True)
            # clean data
            if clean_data:
                df = self.clean_data(df)
            # filter data
            if filter_data:
                df = self.filter_data(df)
            # analyse data
            if analyse_data:
                df = self.analyse_data(df)
            # sort columns alphabetically
            df = df.reindex(sorted(df.columns), axis=1)
            # report people that attempted study
            logger.info('Processed {} reports.', df.shape[0])
        # save to pickle
        if self.save_p:
            gpte.common.save_to_p(self.file_p, df, 'chatgpt data')
        # save to csv
        if self.save_csv:
            df.to_csv(os.path.join(gpte.settings.output_dir, self.file_data_csv),
                      index=False)
            logger.info('Saved data to csv file {}',
                        self.file_data_csv + '.csv')
        # update attribute
        self.data = df
        # return df with data
        return df

    def pdf_to_base64_image(self, file):
        """Turn pages of the PDF file with the report to base64 strings.
        Args:
            file (str): Name of file of the report.

        Returns:
            base64_image (list): List of pages as base64 strings.
        """
        # create full path of the file with the report
        file = os.fsdecode(file)
        full_path = os.path.join(self.files_reports, file)
        f = open(full_path, 'r')
        # each page is 1 base64_image
        base64_image = ['bla0', 'bla1']
        # TODO: turn pdfs into base64 (LZ)
        # close image
        f.close()
        logger.debug('Turned report {} into base64_image.', file)
        return base64_image

    # TODO: call for GPT4-V (PB)
    def ask_gptv(self, file, pages):
        """Receive responses from GPT4-V for all pages at once.
        Args:
            file (str): File with report.
            pages (list): List of pages as base64 strings.

        Returns:
            dataframe: dataframe with responses.
        """
        # build content with multiple images
        # first add a query to the content list 
        content = [{
                      "type": "text",
                      "text": gpte.common.get_configs('query'),
                    }
                   ]
        # populate the list with base64 strings of pages in the report
        for page in pages:
            content.append({
                      "type": "image_url",
                      "image_url": {
                        "url": f"data:image/jpeg;base64,{page}"
                      },
                    })
        # object to store response
        response = None
        # send request to GPT4-V
        try:
            response = self.gpt_client.chat.completions.create(
              model="gpt-4-vision-preview",
              messages=[
                {
                  "role": "user",
                  "content": content
                }
              ],
              max_tokens=300,
            )
            logger.debug('Received response from GPT4-V: {}.', response.choices[0])
        except openai.AuthenticationError:
            logger.error('Incorrect API key provided to OpenAI.')
            return None
        # turn response into a dataframe
        data = {'report': [file], 'response': [response.choices[0]]}
        df = pd.DataFrame(data)
        return df

    # TODO: analysis of data from GPT4-V (PB, LZ)
    def analyse_data(self, df):
        """Analyse responses from GPT4-V for all reports.
        Args:
            df (TYPE): Dataframe with responses from GPT4-V for all reports.

        Returns:
            dataframe: updated dataframe.
        """
        logger.error('Analysis of data not implemented.')
        return df

    def filter_data(self, df):
        """
        Filter data.
        Args:
            df (dataframe): dataframe with data.

        Returns:
            dataframe: updated dataframe.
        """
        logger.error('Filtering data not implemented.')
        # assign to attribute
        self.chatgpt_data = df
        # return df with data
        return df

    def clean_data(self, df):
        """Clean data from unexpected values.

        Args:
            df (dataframe): dataframe with data.

        Returns:
            dataframe: updated dataframe.
        """
        logger.error('Cleaning data not implemented.')
        # assign to attribute
        self.chatgpt_data = df
        # return df with data
        return df

    def show_info(self):
        """
        Output info for data in object.
        """
        logger.info('No info to show.')
