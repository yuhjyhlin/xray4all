#!/usr/bin/env python2
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio
from gi.repository import GdkPixbuf
import os
import sys
import stat
import time

builder = Gtk.Builder()
builder.add_from_file(os.path.realpath(os.path.dirname(__file__)) + "/ui.glade")
listbox_recents = builder.get_object("listbox_recents")
recent_manager = Gtk.RecentManager()
recents = recent_manager.get_items()
recents_count = len(recents)
active_recents_count = 0
img_recents_path = []
img_recents_name = []

def refresh_recents():
    global active_recents_count
    global img_recents_name
    global recents
    recents = recent_manager.get_items()

    for _ in range(active_recents_count):
        listbox_recents.remove(listbox_recents.get_row_at_index(0))

    img_recents_path = []
    img_recents_name = []

    for i in range(recents_count):
        if recents[i].get_uri()[-8:].lower() == ".png" and recents[i].get_uri()[:7] == "file://" and os.path.isfile(recents[i].get_uri()[7:]):
            img_recents_path.append(recents[i].get_uri()[7:])
            img_recents_name.append(recents[i].get_display_name())

    active_recents_count = len(img_recents_name)

    for _ in range(active_recents_count):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        label_name = Gtk.Label()
        label_path = Gtk.Label()
        label_name.set_xalign(0)
        label_path.set_xalign(0)
        label_path.set_opacty(0.5)
        box.set_spacing(6)
        label_name.set_text(img_recents_name[i])
        label_path.set_text(img_recents_path[i])
        box.pack_end(label_path, True, True, 0)
        box.pack_end(label_name, True, True, 0)
        row = Gtk.ListBoxRow()
        row.add(box)
        listbox_recents.add(row)

refresh_recents()

class App(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(
            self,
            application_id="com.filemonmateus.xray4all",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        builder.get_object("about_dialog").connect("delete-event", lambda *_: builder.get_object("about_dialog").hide() or True)
        self.connect("activate", self.activate)

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def activate(self, app):
        window = builder.get_object("window_main")
        window.set_wmclass("xray4all", "xray4all")
        window.set_default_icon_from_file(os.path.realpath(os.path.dirname(__file__)) + "/icon.svg")
        window.set_position(Gtk.WindowPosition.CENTER)
        app.add_window(window)

        appMenu = Gio.Menu()
        appMenu.append("About", "app.about")
        appMenu.append("Quit", "app.quit")

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about_activate)
        app.add_action(about_action)

        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit_activate)
        app.add_action(quit_action)

        app.set_app_menu(appMenu)
        window.show_all()

    def on_about_activate(self, *args):
        builder.get_object("about_dialog").show()

    def on_quit_activate(self, *args):
        self.quit()

def wait(timelapse):
    start = time.time()
    end = start + timelapse

    while end > time.time():
        while Gtk.events_pending():
            Gtk.main_iteration()

class Handler:
    def __init__(self, custom_save_path=None, info_bar_buttons_action_code=0):
        self.custom_save_path = custom_save_path
        self.info_bar_buttons_action_code = info_bar_buttons_action_code
        self.model = "DenseNet121"
        self.img_name = ""
        self.pathologies = ""
        self.show_heatmap = True

    def show_info(self, message, buttons, re_hide=False):
        info_bar = builder.get_object("info_bar")
        label_info_bar = builder.get_object("label_info_bar")
        label_info_bar.set_text(message)
        info_bar.show()

        if re_hide:
            wait(5)
            info_bar.hide()

    def on_btn_info_bar_close_clicked(self, info_bar, params):
        info_bar.hide()

    def on_btn_info_bar_ok_clicked(self, info_bar, params):
        info_bar.hide()

    def scale_image(self, filename):
        return GdkPixbuf.new_from_file_at_size(filename, 120, 120)

    def on_btn_go_back_one_clicked(self, button):
        builder.get_object("window_loading").hide()
        builder.get_object("window_main").show()

    def on_btn_go_back_two_clicked (self, button):
        builder.get_object("window_loading").hide()
        builder.get_object("window_main").show()

    def on_file_picker_activated(self, event):
        print("Event: File picker activated!")
        print("TODO")

    def on_image_picker_file_set(self, file_picker):
        self.img_name = file_picker.get_filename()

        if os.path.splitext(self.img_name)[1].lower() != '.png':
            self.show_info("Invalid image extension. Try a .PNG instead.", False)
            builder.get_object("entry_image").set_text("")
            builder.get_object("btn_analyze").set_sensitive(False)
            file_picker.unselect_all()
            return

        self.img_name.replace(" ", "\\ ").replace("\\", "\\\\")
        builder.get_object("entry_image").set_text(self.img_name)
        builder.get_object("btn_analyze").set_sensitive(True)
        builder.get_object("info_bar").hide()

    def on_btn_open_clicked(self, event):
        if popover.get_visible():
            popover.hide()
        else:
            popover.show_all()

    def reset_ui(self):
        builder.get_object("combobox_model").set_text("")
        builder.get_object("entry_image").set_text("")
        builder.get_object("combobox_pathologies").set_text("")
        builder.get_object("switch_heat_map").set_state(True)

    def on_btn_open_browse_clicked(self, event):
        builder.get_object("file_picker").set_current_folder_uri(os.path.dirname(__file__))
        builder.get_object("file_picker").show_all()
        popover.hide()

    def on_btn_analyze_clicked(self, event):
        img_name = self.img_name.split("/")[-1].replace("//", "")
        builder.get_object("window_main").hide()
        builder.get_object("xray_img_name").set_text(img_name)
        builder.get_object("window_loading").set_position(Gtk.WindowPosition.CENTER)
        builder.get_object("window_loading").show()

    def on_model_changed(self, event):
        self.model = event.get_active_text()

    def on_detectable_pathologies_changed(self, event):
        self.pathologies = event.get_active_text()

    def on_heatmap_switcher_activated(self, switcher, params):
        if switcher.get_active():
            self.show_heatmap = True
        else:
            self.show_heatmap = False

    def on_btn_file_picker_open_clicked(self, image, params):
        print("Event: Open btn clicked!")
        print("TODO")

    def on_btn_file_picker_cancel_clicked(self, event):
        print("Event: Cancel btn clicked!")
        print("TODO")

    def on_btn_file_saver_save_clicked(self, event):
        print("Event: Save btn clicked!")
        print("TODO")

    def on_btn_file_saver_cancel_clicked(self, event):
        print("Event: Cancel btn clicked!")
        print("TODO")

    def on_btn_save_as_clicked(self, event):
        print("Event: Save As btn clicked")
        print("TODO")

        """path = builder.get_object("file_saver").get_filename()

        if path[-8:].lower() != ".png":
            path += ".png"

        self.custom_save_path = path
        builder.get_object("file_saver").hide()
        self.btn_save_clicked(event)"""

popover = Gtk.Popover.new(builder.get_object("btn_open"))
popover.add(builder.get_object("opener_widget"))
builder.connect_signals(Handler())

if __name__ == '__main__':
    app = App()
    app.run(sys.argv)
