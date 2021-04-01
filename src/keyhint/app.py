"""
Cheatsheat for keyboard shortcuts & commands
"""

import importlib.resources
import logging
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gio, GLib, Gtk  # noqa

from keyhint.window import WindowHandler  # noqa

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%H:%M:%S",
    level="WARNING",
)
logger = logging.getLogger(__name__)
# TODO: Store settings:
# https://docs.python.org/3/library/configparser.html
# https://marianochavero.wordpress.com/2012/04/03/short-example-of-gsettings-bindings-in-python/
# https://www.micahcarrick.com/gsettings-python-gnome-3.htm


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="org.example.myapp",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs,
        )
        self.window = None

        self.add_main_option(
            "verbose",
            ord("v"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Verbose log output for debugging",
            None,
        )
        self.add_main_option(
            "hint",
            ord("h"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.STRING,
            "Show hints by specified ID",
            "HINT-ID",
        )
        self.add_main_option(
            "default-hint",
            ord("d"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.STRING,
            "Hint to show in case no hints for active application were found",
            "HINT-ID",
        )

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        if not self.window:
            builder = Gtk.Builder()
            builder.set_application(self)
            with importlib.resources.path(
                "keyhint.resources", "ApplicationWindow.glade"
            ) as p:
                ui = str(p.absolute())
            builder.add_from_file(ui)
            builder.connect_signals(WindowHandler(builder, self.options))

            self.window = builder.get_object("keyhint_app_window")
            self.window.set_application(self)
            self.window.show_all()

        self.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        self.options = options.end().unpack()

        if "verbose" in self.options:
            logging.getLogger().setLevel("DEBUG")
            logger.info("Log level is set to 'DEBUG'")

        logger.debug("CLI Options: " + str(self.options))
        self.activate()
        return 0


def main():
    app = Application()
    app.run(sys.argv)


if __name__ == "__main__":
    main()