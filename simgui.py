# -*- coding: utf-8 -*-
"""
This module includes definition of class SimGui responsible for simulation user interface.
"""


from typing import Dict, Any, Callable
import dearpygui.core as dpgc
import dearpygui.simple as dpgs


class SimGui:
    """ Class for handling application GUI """

    __column_names = ['no', 'name', 'id', 'payload', 'modify', 'delete', '100ms', 'send']
    __column_widths_d = dict(zip(__column_names, [50, 250, 100, 300, 50, 50, 50, 50]))
    __column_items_d = dict(zip(__column_names, ['it_' + name for name in __column_names]))
    __column_items_new_d = dict(zip(__column_names, ['it_' + name + '_new' for name in __column_names]))
    __wnd_width, __wnd_height = 530, 160
    __wnd_main_width, __wnd_main_height = 1000, 600
    __sim_en_btn_width, __sim_en_btn_height = 120, 40
    __add_msg_btn_width, __add_msg_btn_height = 100, 30
    __popup_btn_width, __popup_btn_height = 75, 25
    __margin_10, __margin_30 = 10, 30
    __item_msg_table = 'msg_table'
    __item_simulation_main = 'simulation_main'
    __item_bnt_add_message = 'add_message'
    __item_btn_start_sim = 'btn_start_sim'
    __item_btn_stop_sim = 'btn_stop_sim'
    __hide_label = '##'

    def __init__(self, switch_sim_en_h: Callable, add_msg_h: Callable, delete_msg_h: Callable, modify_msg_h: Callable,
                 get_msg_db_h: Callable, send_msg_trig_h: Callable, version: str) -> None:
        """
        Setups external handlers
        Params:                                                                     type:
        @param switch_sim_en_h: Function enabling/disabling simulation              Callable
        @param add_msg_h: Function adding message to database                       Callable
        @param delete_msg_h: Function deleting message from database                Callable
        @param modify_msg_h: Function modifying message in database                 Callable
        @param get_msg_db_h: Function returning messages database                   Callable
        @param send_msg_trig_h: Function triggering sending message                 Callable
        @param version: Application version                                         str
        @return: None
        """

        self.__switch_sim_en_h = switch_sim_en_h
        self.__add_msg_h = add_msg_h
        self.__delete_msg_h = delete_msg_h
        self.__modify_msg_h = modify_msg_h
        self.__get_msg_config_h = get_msg_db_h
        self.__send_msg_trig_h = send_msg_trig_h
        self.__version = version

    def __display_table(self) -> None:
        """
        Displays messages configuration from database
        Params:                                                                     type:
        @return: None
        """

        """ Configure columns """
        dpgc.add_managed_columns(name=self.__item_msg_table, columns=len(self.__column_names),
                                 parent=self.__item_simulation_main)

        for name, index in zip(self.__column_names, range(len(self.__column_widths_d))):
            dpgc.add_text(name=name)
            dpgc.set_managed_column_width(item=self.__item_msg_table, column=index,
                                          width=self.__column_widths_d[name])

        """ Add rows """
        msg_config_df = self.__get_msg_config_h()
        for (df_row_id, row), index in zip(msg_config_df.iterrows(), range(msg_config_df.shape[0])):

            dpgc.add_text(str(index))

            dpgc.add_input_text(name=self.__hide_label + self.__column_items_d['name'] + str(index),
                                width=self.__column_widths_d['name'] - self.__margin_10,
                                enabled=False)
            dpgc.set_value(self.__hide_label + self.__column_items_d['name'] + str(index), str(row['name']))

            dpgc.add_input_text(name=self.__hide_label + self.__column_items_d['id'] + str(index),
                                width=self.__column_widths_d['id'] - self.__margin_10,
                                enabled=False)
            dpgc.set_value(self.__hide_label + self.__column_items_d['id'] + str(index), str(row['id']))

            dpgc.add_input_text(name=self.__hide_label + self.__column_items_d['payload'] + str(index),
                                width=self.__column_widths_d['payload'] - self.__margin_10,
                                enabled=False)
            dpgc.set_value(self.__hide_label + self.__column_items_d['payload'] + str(index), str(row['payload']))

            dpgc.add_button(self.__hide_label + self.__column_items_d['modify'] + str(index), small=False, label=' ... ',
                            callback=self.__btn_modify_msg_clbk,
                            callback_data={'index': index, 'source_checkbox': False})

            dpgc.add_button(self.__hide_label + self.__column_items_d['delete'] + str(index), small=False, label='  x  ',
                            callback=self.__btn_del_msg_clbk,
                            callback_data=index)

            dpgc.add_checkbox(name=self.__hide_label + self.__column_items_d['100ms'] + str(index),
                              callback=self.__btn_modify_msg_clbk,
                              callback_data={'index': index, 'source_checkbox': True})
            dpgc.set_value(self.__hide_label + self.__column_items_d['100ms'] + str(index), bool(row['period_en']))

            dpgc.add_button(self.__hide_label + self.__column_items_d['send'] + str(index), label='  >  ',
                            callback=self.__btn_send_clbk,
                            callback_data=index)

        dpgc.add_separator()

        """ Add new message pop up """
        with dpgs.popup(popupparent='btn_add_msg', name=self.__item_bnt_add_message, modal=True,
                        mousebutton=dpgc.mvMouseButton_Left):

            dpgc.add_text('Name:\t\t')
            dpgc.add_same_line()
            dpgc.add_input_text(name=self.__hide_label + self.__column_items_d['name'] + '_new',
                                width=self.__column_widths_d['payload'] + self.__margin_30,
                                hint='e.g. Network Management')

            dpgc.add_text('Id:  \t\t')
            dpgc.add_same_line()
            dpgc.add_input_text(name=self.__hide_label + self.__column_items_d['id'] + '_new',
                                width=self.__column_widths_d['payload'] + self.__margin_30, hint='e.g. 0x567')

            dpgc.add_text('Payload: \t')
            dpgc.add_same_line()
            dpgc.add_input_text(name=self.__hide_label + self.__column_items_d['payload'] + '_new',
                                width=self.__column_widths_d['payload'] + self.__margin_30,
                                hint='e.g. 0x50 0x40 0x30 0x20 0x10 0x00 0x00 0x00')

            dpgc.add_button(name='btn_add_msg_confirm', label='Add', width=self.__popup_btn_width,
                            height=self.__popup_btn_height, callback=self.__btn_add_msg_clbk)
            dpgc.add_same_line()

            dpgc.add_button(name='btn_add_msg_cancel', label='Cancel', width=self.__popup_btn_width,
                            height=self.__popup_btn_height, callback=self.__btn_add_msg_clbk, callback_data=True)

    def __update_msg_table(self) -> None:
        """
        Reloads messages configuration table
        Params:                                                                     type:
        @return: None
        """

        dpgc.delete_item(self.__item_msg_table)
        dpgc.delete_item(self.__item_bnt_add_message)
        self.__display_table()

    def __btn_switch_sim_en_clbk(self, sender: str, sim_en: bool) -> None:
        """
        Callback for start/stop simulation buttons
        Params:                                                                     type:
        @param sender: Not used                                                     str
        @param sim_en: Enable simulation                                            bool
        @return: None
        """

        dpgc.configure_item(self.__item_btn_start_sim, enabled=not sim_en)
        dpgc.configure_item('btn_stop_sim', enabled=sim_en)
        self.__switch_sim_en_h(sim_en=sim_en)

    def __btn_add_msg_clbk(self, sender: str, is_cancel=False) -> None:
        """
        Callback for add message/cancel buttons
        Params:                                                                     type:
        @param sender: Not used                                                     str
        @param is_cancel: Adding message canceled                                   bool
        @return: None
        """

        if is_cancel:
            dpgc.close_popup(self.__item_bnt_add_message)
        else:
            if self.__add_msg_h(name=dpgc.get_value(self.__hide_label + self.__column_items_new_d['name']),
                                msg_id=dpgc.get_value(self.__hide_label + self.__column_items_new_d['id']),
                                payload=dpgc.get_value(self.__hide_label + self.__column_items_new_d['payload'])):
                self.__update_msg_table()
            else:
                """ Provided message is invalid """
            pass

    def __btn_del_msg_clbk(self, sender: str, index: int) -> None:
        """
        Callback for delete message buttons
        Params:                                                                     type:
        @param sender: Not used                                                     str
        @param index: Index of message to be deleted                                int
        @return: None
        """

        self.__delete_msg_h(index=index)
        self.__update_msg_table()

    def __btn_modify_msg_clbk(self, sender: str, data: Dict[str, Any]) -> None:
        """
        Callback for modify message buttons
        Params:                                                                     type:
        @param sender: Not used                                                     str
        @param data: Modified message                                               Dict[str, Any]
        @return: None
        """

        """ Check if this is first step for modification - clicked modify button """
        if not (dpgc.get_item_configuration(self.__hide_label + self.__column_items_d['name'] +
                                            str(data['index'])))['enabled'] and not data['source_checkbox']:

            """ Clicked modify button - enable editing"""
            dpgc.configure_item(self.__hide_label + self.__column_items_d['name'] + str(data['index']), enabled=True)
            dpgc.configure_item(self.__hide_label + self.__column_items_d['id'] + str(data['index']), enabled=True)
            dpgc.configure_item(self.__hide_label + self.__column_items_d['payload'] + str(data['index']), enabled=True)
            dpgc.configure_item(self.__hide_label + self.__column_items_d['modify'] + str(data['index']), label=' /ok ')
        else:
            """ Save updated values """
            if self.__modify_msg_h(index=data['index'],
                                   name=dpgc.get_value(self.__hide_label + self.__column_items_d['name'] +
                                                       str(data['index'])),
                                   msg_id=dpgc.get_value(self.__hide_label + self.__column_items_d['id'] +
                                                         str(data['index'])),
                                   payload=dpgc.get_value(self.__hide_label + self.__column_items_d['payload'] +
                                                          str(data['index'])),
                                   period_en=dpgc.get_value(self.__hide_label + self.__column_items_d['100ms'] +
                                                            str(data['index']))):
                self.__update_msg_table()
            else:
                """ Provided message is invalid """
                pass

    def __btn_send_clbk(self, sender: str, index: int) -> None:
        """
        Callback for send message buttons
        Params:                                                                     type:
        @param sender: Not used                                                     str
        @param index: Index of message to be sent                                   int
        @return: None
        """

        """ Callback for send message buttons """
        self.__send_msg_trig_h(index=index)

    """ ============================================= Class interface ============================================= """

    def run_gui(self) -> None:
        """
        Starts application gui
        Params:                                                                     type:
        @return: None
        """

        with dpgs.window(name=self.__item_simulation_main, width=self.__wnd_width, height=self.__wnd_height):
            dpgc.set_main_window_size(self.__wnd_main_width, self.__wnd_main_height)
            dpgc.set_main_window_title('canvector' + ' ' + self.__version)
            dpgc.add_indent()
            dpgc.add_button(name=self.__item_btn_start_sim, label='Start simulation', width=self.__sim_en_btn_width,
                            height=self.__sim_en_btn_height, callback=self.__btn_switch_sim_en_clbk,
                            callback_data=True, enabled=True)
            dpgc.add_same_line()
            dpgc.add_button(name=self.__item_btn_stop_sim, label='Stop simulation', width=self.__sim_en_btn_width,
                            height=self.__sim_en_btn_height, callback=self.__btn_switch_sim_en_clbk,
                            callback_data=False, enabled=False)
            dpgc.add_spacing()
            dpgc.add_button(name='btn_add_msg', label='Add message', width=self.__add_msg_btn_width,
                            height=self.__add_msg_btn_height)

            dpgc.add_spacing()
            dpgc.add_separator()

            self.__display_table()

        dpgc.start_dearpygui(primary_window=self.__item_simulation_main)
