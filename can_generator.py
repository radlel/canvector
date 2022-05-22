# -*- coding: utf-8 -*-
"""
This application ia a CAN generator which can be used with Vector hardware.
Messages can be added, removed and modified using GUI. Also, they can be
sent on trigger or periodically every 100ms. All changes in messages
database are immediately saved in candb\db.csv.

This application requires CANoe installed and properly configured - it uses
CANoe configuration.

No Vector license is needed to run this application and send CAN frames
by Vector hardware.

Execution:
    $ python can_generator.py
"""


__author__ = 'Radoslaw Lelito'
__email__ = 'radoslaw.lelito@gmail.com'
__date__ = '2020/06/01'
__license__ = 'MIT'
__version__ = '1.0.1'


import can
import schedule
import time
from threading import Thread

from dbman import DataBaseMan
from simgui import SimGui


class Simulation:
    """ Class for simulation handling """

    __vect_bus_type = 'vector'
    __vect_app_name = 'CANoe'
    __vect_channel = 0
    __vect_bitrate = 500000

    def __init__(self) -> None:
        self.__sim_active = False
        self.__bus = self.__config_vector_interface()
        self.__database_man = DataBaseMan()
        self.__sim_gui = SimGui(switch_sim_en_h=self.__switch_sim_en,
                                add_msg_h=self.__database_man.add_msg,
                                delete_msg_h=self.__database_man.delete_msg,
                                modify_msg_h=self.__database_man.modify_msg,
                                get_msg_db_h=self.__database_man.get_msg_db,
                                send_msg_trig_h=self.__send_msg_trigger,
                                version=__version__)
        self.__sim_enabled = False

    def __switch_sim_en(self, sim_en: bool) -> None:
        """
        Enables or disables simulation
        Params:                                                                     type:
        @param sim_en: Simulation enable                                            bool
        @return: None
        """

        self.__sim_active = sim_en

    def __send_msgs_periodic(self) -> None:
        """
        Sends messages from database if periodic transmission is enabled
        Params:                                                                     type:
        @return: None
        """

        msg_config_df = self.__database_man.get_msg_db()
        for df_row_id, row in msg_config_df.iterrows():
            """ Check if periodic transmission is enabled """
            if row['period_en']:
                """ Send message """
                self.__send_msg(msg_id=row['id'], payload=row['payload'])
            else:
                """ Periodic transmission not enabled - do nothing """
                pass

    def __send_msg_trigger(self, index: int) -> None:
        """
        Sends specified message once
        Params:                                                                     type:
        @param index: Index of the message in database                              int
        @return: None
        """

        msg_db_df = self.__database_man.get_msg_db()
        self.__send_msg(msg_id=msg_db_df.at[index, 'id'], payload=msg_db_df.at[index, 'payload'])

    def __send_msg(self, msg_id: str, payload: str) -> None:
        """
        Performs sending message
        Params:                                                                     type:
        @param msg_id: Id of CAN message                                            int
        @param payload: Payload of CAN message                                      str
        @return: None
        """

        if self.__sim_active:
            msg = can.Message(arbitration_id=int(msg_id, 16), data=[int(B, 16) for B in payload.split(' ')],
                              extended_id=False)
            try:
                self.__bus.flush_tx_buffer()
                self.__bus.send(msg)
                print('Message sent: [{}] {}'.format(msg_id, payload))
            except (can.CanError, AttributeError):
                print('Error! Message not sent:', msg_id)
                pass
        else:
            """ Simulation is not active, do nothing """
            pass

    def __scheduler(self) -> None:
        """
        Triggers sending messages every 100ms if configured
        Params:                                                                     type:
        @return: None
        """

        schedule.every(0.1).seconds.do(self.__send_msgs_periodic)
        while True:
            schedule.run_pending()
            time.sleep(0.01)

    @staticmethod
    def __config_vector_interface() -> can.interface.Bus:
        """
        Performs Vector hardware configuration
        Params:                                                                     type:
        @return: Configured bus object                                              can.interface.Bus
        """
        try:
            return can.interface.Bus(bustype=Simulation.__vect_bus_type, app_name=Simulation.__vect_app_name,
                                     channel=Simulation.__vect_channel, bitrate=Simulation.__vect_bitrate)

        except ImportError:
            print('Could not import Vector hardware configuration!')

    """ ============================================= Class interface ============================================= """

    def run(self) -> None:
        """
        Starts simulation
        Params:                                                                     type:
        @return: None
        """

        Thread(target=self.__sim_gui.run_gui).start()
        Thread(target=self.__scheduler).start()


if __name__ == '__main__':
    sim = Simulation()
    sim.run()
