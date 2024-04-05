from time import monotonic
from pathlib import Path
from os.path import getsize

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Static, Switch, TextLog, Input, DataTable

DIR = Path('/home/leonard/hello/python/Doornifer/textual/docs/examples/tutorial')
clipNames = list(map(lambda f: f.name, DIR.iterdir()))

class ClipList(DataTable):
    def on_mount(self):
        self.add_columns('Name', 'Length')
        self.add_rows(list(zip(clipNames, map(getsize, DIR.iterdir()))))

    def refine(self, search):
        # with Path('/tmp/DEBUGGING.txt').open('w') as out:
        #     print('something happened', file=out)
        #     print(search, file=out)
        #     print(search.key, file=outf)
        self.clear()
        applicable = sorted(filter(lambda c: search in c, clipNames), key=lambda n: n.index(search))
        self.add_rows(list(zip(applicable, map(getsize, [DIR.parent / f for f in applicable]))))

class Search(Input):
    cliplist = None
    # def on_event(self, event):
    def _on_key(self, event):
        # with Path('/tmp/DEBUGGING.txt').open('w') as out:
        #     print('event happened', file=out)
        #     print(event, file=out)

        self.cliplist.refine(event.key)
        return super().on_event(event)


class DoorniferApp(App):
    CSS_PATH = "main.css"

    BINDINGS = [
        # ("d", "toggle_dark", "Toggle dark mode"),
        # ("a", "add_stopwatch", "Add"),
        # ("r", "remove_stopwatch", "Remove"),
    ]

    def compose(self) -> ComposeResult:
        """Called to add widgets to the app."""
        yield Header(show_clock=True)
        yield Footer()
        yield Search(placeholder='Clip')
        yield ClipList()

    def on_mount(self) -> None:
        table = self.query_one(ClipList)

        search = self.query_one(Search)
        search.cliplist = table
        # search._on_key = lambda e: table.refine(e.key)
        # search.on_event(table.refine)
        # search.on
        # search._on_key = lambda e: print(e.key, file=out)
        # print(e.key)


if __name__ == "__main__":
    app = DoorniferApp()
    app.run()
