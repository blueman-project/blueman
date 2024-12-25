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
    def __init__(self, rowdata: Iterable[ListDataDict], headers_visible: bool = True, visible: bool = False) -> None:
        super().__init__(headers_visible=headers_visible, visible=visible)
        self.set_name("GenericList")
        self.selection = self.get_selection()
        self._load(rowdata)

    def _load(self, data: Iterable[ListDataDict]) -> None:
        # Mapping of internal rowdata id to the ListStore column number and TreeViewColumn
        self.list_col_order: dict[str, int] = {}
        self.view_columns: dict[str, Gtk.TreeViewColumn] = {}

        list_col_types = [row["type"] for row in data]

        self.liststore = Gtk.ListStore(*list_col_types)
        self.filter = self.liststore.filter_new()
        self.set_model(self.filter)

        for list_col_num, row in enumerate(data):
            self.list_col_order[row["id"]] = list_col_num

            if "renderer" not in row:
                continue

            view_column = Gtk.TreeViewColumn()
            view_column.pack_start(row["renderer"], True)
            view_column.set_attributes(row["renderer"], **row["render_attrs"])

            if "view_props" in row:
                view_column.set_properties(**row["view_props"])

            if "celldata_func" in row:
                func, user_data = row["celldata_func"]
                view_column.set_cell_data_func(row["renderer"], func, user_data)

            self.view_columns[row["id"]] = view_column
            self.append_column(view_column)

    def selected(self) -> Gtk.TreeIter | None:
        list_model, tree_iter = self.selection.get_selected()
        if tree_iter is not None:
            tree_iter = list_model.convert_iter_to_child_iter(tree_iter)
        return tree_iter

    def delete(self, tree_iter: Gtk.TreeIter) -> bool:
        if self.liststore.iter_is_valid(tree_iter):
            self.liststore.remove(tree_iter)
            return True
        else:
            return False

    def _add(self, **list_columns: object) -> Collection[object]:
        items: dict[int, object] = {}
        for col_id, list_col_num in self.list_col_order.items():
            items[list_col_num] = None

        for col_id, col_value in list_columns.items():
            if col_id in self.list_col_order:
                items[self.list_col_order[col_id]] = col_value
            else:
                raise Exception(f"Invalid key {col_id}")

        return items.values()

    def append(self, **list_columns: object) -> Gtk.TreeIter:
        vals = self._add(**list_columns)
        return self.liststore.append(vals)

    def prepend(self, **list_columns: object) -> Gtk.TreeIter:
        vals = self._add(**list_columns)
        return self.liststore.prepend(vals)

    def set(self, tree_iter: Gtk.TreeIter, **list_columns: object) -> None:
        for col_id, col_value in list_columns.items():
            self.liststore.set(tree_iter, self.list_col_order[col_id], col_value)

    def get(self, tree_iter: Gtk.TreeIter, *items: str) -> dict[str, Any]:
        data = {}
        if not items:
            columns = [(col_id, self.list_col_order[col_id]) for col_id in self.list_col_order]
        else:
            columns = [(col_id, self.list_col_order[col_id]) for col_id in items if col_id in self.list_col_order]

        for col_id, list_col_num in columns:
            data[col_id] = self.liststore.get_value(tree_iter, list_col_num)
        return data

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
