# This Python file uses the following encoding: utf-8
#
# SPDX-FileCopyrightText: 2021-2022 Raphaël Doursenaud <rdoursenaud@free.fr>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Main window
"""

from dearpygui import dearpygui as dpg
from dearpygui.demo import show_demo

import gui.config
import gui.logger
import gui.windows.log
from gui.config import DEBUG


def create() -> None:
    with dpg.window(
            tag='main_win',
            label="MIDI Explorer",
            width=1920,
            height=1080,
            no_close=True,
            collapsed=False,
    ):
        gui.config.create_selectors()

        with dpg.menu_bar():
            with dpg.menu(label="Configuration"):
                dpg.add_menu_item(label="Load", callback=gui.config.load)
                dpg.add_menu_item(label="Save", callback=gui.config.save)
                dpg.add_menu_item(label="Save as", callback=gui.config.saveas)
                dpg.add_menu_item(label="Reset", callback=gui.config.clear)

            with dpg.menu(label="Display"):
                dpg.add_menu_item(label="Toggle Fullscreen (F11)", callback=dpg.toggle_viewport_fullscreen)
                dpg.add_menu_item(label="Toggle Log (F12)", callback=gui.windows.log.toggle)

            with dpg.menu(label="Help"):
                if DEBUG:
                    with dpg.menu(label="Debug"):
                        dpg.add_menu_item(label="Show About", callback=lambda: dpg.show_tool(dpg.mvTool_About))
                        dpg.add_menu_item(label="Show Metrics", callback=lambda: dpg.show_tool(dpg.mvTool_Metrics))
                        dpg.add_menu_item(label="Show Documentation", callback=lambda: dpg.show_tool(dpg.mvTool_Doc))
                        dpg.add_menu_item(label="Show Debug", callback=lambda: dpg.show_tool(dpg.mvTool_Debug))
                        dpg.add_menu_item(label="Show Style Editor", callback=lambda: dpg.show_tool(dpg.mvTool_Style))
                        dpg.add_menu_item(label="Show Font Manager", callback=lambda: dpg.show_tool(dpg.mvTool_Font))
                        dpg.add_menu_item(label="Show Item Registry",
                                          callback=lambda: dpg.show_tool(dpg.mvTool_ItemRegistry))
                        dpg.add_menu_item(label="Show ImGui Demo", callback=lambda: dpg.show_imgui_demo())
                        dpg.add_menu_item(label="Show ImPlot Demo", callback=lambda: dpg.show_implot_demo())
                        dpg.add_menu_item(label="Show Dear PyGui Demo", callback=lambda: show_demo())
                dpg.add_menu_item(label="About", callback=gui.windows.about.toggle)
