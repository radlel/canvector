# -*- coding: utf-8 -*-
"""
This module includes definition of class DataBaseMan responsible for can messages database management.
"""


import os
from enum import Enum
import pandas as pd


DB_FILE_PATH = r'candb\db.csv'


class MsgValid(Enum):
    VALID = 0,
    INVALID = 1


class DataBaseMan:
    """ Class for messages database management """

    """ Definition of messages database headers """
    __DB_H_NAME, __DB_H_ID, __DB_H_PAYLOAD, __DB_H_PERIOD_EN, __DB_H_PERIOD = \
        'name', 'id', 'payload', 'period_en', 'period'
    __DB_DF_HEADERS = [__DB_H_NAME, __DB_H_ID, __DB_H_PAYLOAD, __DB_H_PERIOD_EN, __DB_H_PERIOD]

    def __init__(self) -> None:
        self.__msg_db_df = None
        self.__create_msg_db_file()
        self.__load_msg_db_from_file()

    def __create_msg_db_file(self) -> None:
        """
        Creates db file if it does not exist
        Params:                                                                     type:
        @return: None
        """

        if not os.path.exists(DB_FILE_PATH):
            self.__msg_db_df = pd.DataFrame(columns=self.__DB_DF_HEADERS)
            if not os.path.exists(os.path.dirname(DB_FILE_PATH)):
                os.mkdir(os.path.dirname(DB_FILE_PATH))
            self.__msg_db_df.to_csv(DB_FILE_PATH, index=False)
            print('Created db file: {}'.format(DB_FILE_PATH))
        else:
            """ Db file already exists """
            pass

    def __load_msg_db_from_file(self) -> None:
        """
        Loads configuration from db file
        Params:                                                                     type:
        @return: None
        """

        self.__msg_db_df = pd.read_csv(DB_FILE_PATH)
        print('Loaded db file:\n{}'.format(self.__msg_db_df))

    def __save_msg_db_to_file(self) -> None:
        """
        Saves configuration to file
        Params:                                                                     type:
        @return: None
        """

        self.__msg_db_df.to_csv(DB_FILE_PATH + '.temp', index=False)
        os.remove(DB_FILE_PATH)
        os.rename(DB_FILE_PATH + '.temp', DB_FILE_PATH)

    def __update_msg_db(self, new_msg_db: pd.DataFrame) -> None:
        """
        Updates msg configuration
        Params:                                                                     type:
        @param new_msg_db: New database                                             pd.DataFrame
        @return: None
        """

        self.__msg_db_df = new_msg_db
        self.__save_msg_db_to_file()

    @staticmethod
    def __is_msg_valid(msg_id: str, payload: str) -> MsgValid:
        """
        Checks if message is valid
        Params:                                                                     type:
        @param msg_id: Message id                                                   str
        @param payload: Message payload                                             str
        @return: Verdict if message is valid                                        MsgValid
        """

        if msg_id.count('0x') == 1 and len(msg_id) > 2:
            """ Provided msg id contains hex symbol as expected """
            try:
                """ Check if provided id contains only allowed characters """
                hex_value = int(msg_id, 16)
            except ValueError:
                """ Provided value contains invalid characters """
                print('Message INVALID! Provided msg id contains invalid characters')
            else:
                """ Provided id contains allowed characters, check if payload is in correct format """
                pld_char_len = len(payload)
                expected_values_num = int((pld_char_len + 1) / 5)
                spaces_num, hex_num = payload.count(' '), payload.count('0x')

                if ((pld_char_len + 1) % 5 == 0 and spaces_num == expected_values_num - 1 and
                        hex_num == expected_values_num and expected_values_num <= 8):
                    """ Payload is in correct format, check if it contains only allowed characters """
                    try:
                        hex_values = [int(val, 16) for val in payload.split(sep=' ')]
                    except ValueError:
                        """ Provided values contain invalid characters """
                        print('Message INVALID! Provided msg payload contains invalid characters')
                    else:
                        """ Provided payload is correct """
                        return MsgValid.VALID
                else:
                    """ Provided payload is in incorrect format """
                    print('Message INVALID! Provided msg payload is in incorrect format')
        else:
            """ Provided msg id not in hex """
            print('Message INVALID! Provided msg id is not valid hex value')

        return MsgValid.INVALID

    """ ============================================= Class interface ============================================= """

    def add_msg(self, name: str, msg_id: str, payload: str) -> bool:
        """
        Adds new message to database
        Params:                                                                     type:
        @param name: Message name                                                   str
        @param msg_id: Message id                                                   str
        @param payload: Message payload                                             str
        @return: Information if operation was successful                            bool
        """

        if MsgValid.VALID == self.__is_msg_valid(msg_id=msg_id, payload=payload):
            """ Provided message is valid """
            new_msg_db_df = self.__msg_db_df.append(pd.DataFrame(([[name, msg_id, payload, False, str(100)]]),
                                                                 columns=self.__DB_DF_HEADERS), ignore_index=True)
            self.__update_msg_db(new_msg_db=new_msg_db_df)
            print('Added new message to db file:\n{}'.format(new_msg_db_df.iloc[[-1]]))
            return True
        else:
            """ Provided message is invalid """
            print('Message not added to db file')
            return False

    def delete_msg(self, index: int) -> None:
        """
        Removes message from database
        Params:                                                                     type:
        @param index: Index of the message in database                              int
        @return: None
        """

        new_msg_config_df = self.__msg_db_df.drop(index=index)
        new_msg_config_df.reset_index(drop=True, inplace=True)
        self.__update_msg_db(new_msg_db=new_msg_config_df)
        print('Deleted message from db file')

    def modify_msg(self, index: int, name: str, msg_id: str, payload: str, period_en: bool) -> bool:
        """
        Modifies message in database
        Params:                                                                     type:
        @param index: Index of the message in database                              int
        @param name: Message name                                                   str
        @param msg_id: Message id                                                   str
        @param payload: Message payload                                             str
        @param period_en: Period transmission enabled                               bool
        @return: Information if operation was successful                            bool
        """

        if MsgValid.VALID == self.__is_msg_valid(msg_id=msg_id, payload=payload):
            upd_msg_config_df = self.__msg_db_df
            upd_msg_config_df.at[index, self.__DB_H_NAME] = name
            upd_msg_config_df.at[index, self.__DB_H_ID] = msg_id
            upd_msg_config_df.at[index, self.__DB_H_PAYLOAD] = payload
            upd_msg_config_df.at[index, self.__DB_H_PERIOD_EN] = period_en
            self.__update_msg_db(new_msg_db=upd_msg_config_df)
            print('Modified message in db file:\n{}'.format(upd_msg_config_df.iloc[[index]]))
            return True
        else:
            """ Provided message is invalid """
            print('Message not updated in db file')
            return False

    def get_msg_db(self) -> pd.DataFrame:
        """
        Provides messages database
        Params:                                                                     type:
        @return: None
        """

        return self.__msg_db_df
