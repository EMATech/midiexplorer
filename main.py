# This Python file uses the following encoding: utf-8
#
# SPDX-FileCopyrightText: 2021-2022 Raphaël Doursenaud <rdoursenaud@free.fr>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
`MIDI Explorer`
===============

* Author(s): Raphaël Doursenaud <rdoursenaud@free.fr>
"""

import os.path

import dearpygui.dearpygui as dpg  # https://dearpygui.readthedocs.io/en/latest/

import gui.logger
import gui.windows.about
import gui.windows.conn
import gui.windows.gen
import gui.windows.log
import gui.windows.main
import gui.windows.probe
import midi
from gui.config import DEBUG, INIT_FILENAME, START_TIME
from midi.ports import lock, queue

if __name__ == '__main__':
    dpg.create_context()

    # Initialize logger ASAP
    gui.windows.log.create()
    logger = gui.logger.Logger('log_win')
    if DEBUG:
        logger.log_level = 0  # TRACE
    else:
        logger.log_level = 2  # INFO
    logger.log_debug(f"Application started at {START_TIME}")

    midi.init()

    ###
    # DOAR PYGUI WINDOWS
    ###
    gui.windows.about.create()
    gui.windows.main.create()
    gui.windows.conn.create()
    gui.windows.probe.create()
    if DEBUG:
        gui.windows.gen.create()

    if not DEBUG:
        if os.path.exists(INIT_FILENAME):
            dpg.configure_app(init_file=INIT_FILENAME)

    gui.windows.conn.refresh_midi_ports()

    with dpg.handler_registry():
        dpg.add_key_press_handler(key=122, callback=dpg.toggle_viewport_fullscreen)  # Fullscreen on F11
        dpg.add_key_press_handler(key=123, callback=gui.windows.log.toggle)  # Log on F12

    ###
    # DEAR PYGUI SETUP
    ###

    # Fonts. https://dearpygui.readthedocs.io/en/latest/documentation/fonts.html

    with dpg.font_registry():
        dpg.add_font('fonts/Roboto-Regular.ttf', 14, tag='default_font')
        dpg.add_font('fonts/RobotoMono-Regular.ttf', 14, tag='mono_font')

    dpg.bind_font('default_font')

    log_win_textbox = dpg.get_item_children('log_win', slot=1)[2]
    dpg.bind_item_font(log_win_textbox, 'mono_font')

    if DEBUG:
        dpg.bind_item_font('probe_midi_mode', 'mono_font')
    dpg.bind_item_font('probe_status_container', 'mono_font')
    dpg.bind_item_font('probe_controllers_container', 'mono_font')
    if DEBUG:
        dpg.bind_item_font('probe_sysex_container', 'mono_font')
    dpg.bind_item_font('probe_notes_container', 'mono_font')

    dpg.bind_item_font('probe_data_table_headers', 'mono_font')
    dpg.bind_item_font('probe_data_table', 'mono_font')

    dpg.create_viewport(title='MIDI Explorer', width=1920, height=1080)

    # Icons must be set before showing viewport (Can also be set when instantiating the viewport)
    dpg.set_viewport_small_icon('icons/midiexplorer.ico')
    dpg.set_viewport_large_icon('icons/midiexplorer.ico')

    # TODO: Custom theme?

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window('main_win', True)

    ###
    # MAIN LOOP
    ###
    while dpg.is_dearpygui_running():  # Replaces dpg.start_dearpygui()
        # TODO: Use a generic event handler with subscribe pattern instead?

        if dpg.get_value('input_mode') == 'Polling':
            with lock:
                gui.windows.conn.poll_processing()

        while not queue.empty():
            gui.windows.conn.handle_received_data(*queue.get())

        gui.windows.probe.update_blink_status()

        dpg.render_dearpygui_frame()

    dpg.destroy_context()
