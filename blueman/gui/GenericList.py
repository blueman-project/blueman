from typing import Any, TypedDict
from collections.abc import Iterable, Mapping, Callable, Collection

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class _ListDataDictBase(TypedDict):
    id: str
    type: type


class ListDataDict(_ListDataDictBase, total=False):
    renderer: Gtk.CellRenderer
    render_attrs: Mapping[str, int]
    view_props: Mapping[str, object]
    celldata_func: tuple[Callable[[Gtk.TreeViewColumn, Gtk.CellRenderer, Gtk.TreeModelFilter, Gtk.TreeIter, Any],
                                  None], Any]


# noinspection PyAttributeOutsideInit
class GenericList(Gtk.TreeView):
    def __init__(self, data: Iterable[ListDataDict], headers_visible: bool = True, visible: bool = False) -> None:
        super().__init__(headers_visible=headers_visible, visible=visible)
        self.set_name("GenericList")
        self.selection = self.get_selection()
        self._load(data)

    def _load(self, data: Iterable[ListDataDict]) -> None:
        self.ids: dict[str, int] = {}
        self.columns: dict[str, Gtk.TreeViewColumn] = {}

        types = [row["type"] for row in data]

        self.liststore = Gtk.ListStore(*types)
        self.filter = self.liststore.filter_new()
        self.set_model(self.filter)

        for i, row in enumerate(data):
            self.ids[row["id"]] = i

            if "renderer" not in row:
                continue

            column = Gtk.TreeViewColumn()
            column.pack_start(row["renderer"], True)
            column.set_attributes(row["renderer"], **row["render_attrs"])

            if "view_props" in row:
                column.set_properties(**row["view_props"])

            if "celldata_func" in row:
                func, user_data = row["celldata_func"]
                column.set_cell_data_func(row["renderer"], func, user_data)

            self.columns[row["id"]] = column
            self.append_column(column)

    def selected(self) -> Gtk.TreeIter | None:
        model, tree_iter = self.selection.get_selected()
        if tree_iter is not None:
            tree_iter = model.convert_iter_to_child_iter(tree_iter)
        return tree_iter

    def delete(self, tree_iter: Gtk.TreeIter) -> bool:
        if self.liststore.iter_is_valid(tree_iter):
            self.liststore.remove(tree_iter)
            return True
        else:
            return False

    def _add(self, **columns: object) -> Collection[object]:
        items: dict[int, object] = {}
        for k, v in self.ids.items():
            items[v] = None

        for k, val in columns.items():
            if k in self.ids:
                items[self.ids[k]] = val
            else:
                raise Exception(f"Invalid key {k}")

        return items.values()

    def append(self, **columns: object) -> Gtk.TreeIter:
        vals = self._add(**columns)
        return self.liststore.append(vals)

    def prepend(self, **columns: object) -> Gtk.TreeIter:
        vals = self._add(**columns)
        return self.liststore.prepend(vals)

    def set(self, tree_iter: Gtk.TreeIter, **cols: object) -> None:
        for k, v in cols.items():
            self.liststore.set(tree_iter, self.ids[k], v)

    def get(self, tree_iter: Gtk.TreeIter, *items: str) -> dict[str, Any]:
        row_data = {}
        if not items:
            columns = [(name, self.ids[name]) for name in self.ids]
        else:
            columns = [(name, self.ids[name]) for name in items if name in self.ids]

        for name, colid in columns:
            row_data[name] = self.liststore.get_value(tree_iter, colid)
        return row_data

    def get_iter(self, path: Gtk.TreePath | None) -> Gtk.TreeIter | None:
        if path is None:
            return None

        try:
            return self.liststore.get_iter(path)
        except ValueError:
            return None

    def clear(self) -> None:
        self.liststore.clear()

    def compare(self, iter_a: Gtk.TreeIter | None, iter_b: Gtk.TreeIter | None) -> bool:
        if iter_a is not None and iter_b is not None:
            assert self.liststore is not None
            return self.liststore.get_path(iter_a) == self.liststore.get_path(iter_b)
        else:
            return False
