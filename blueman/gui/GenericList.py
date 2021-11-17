from typing import Dict, Optional, TYPE_CHECKING, Iterable, Mapping, Callable, Tuple, Union, Collection, List, Any

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


if TYPE_CHECKING:
    from typing_extensions import TypedDict

    class _ListDataDictBase(TypedDict):
        id: str
        type: type

    class ListDataDict(_ListDataDictBase, total=False):
        renderer: Gtk.CellRenderer
        render_attrs: Mapping[str, int]
        view_props: Mapping[str, object]
        celldata_func: Tuple[Callable[[Gtk.TreeViewColumn, Gtk.CellRenderer, Gtk.TreeModelFilter, Gtk.TreeIter, Any],
                                      None], Any]
else:
    ListDataDict = dict


# noinspection PyAttributeOutsideInit
class GenericList(Gtk.TreeView):
    def __init__(self, data: Iterable[ListDataDict], headers_visible: bool = True, visible: bool = False) -> None:
        super().__init__(headers_visible=headers_visible, visible=visible)
        self.set_name("GenericList")
        self.selection = self.get_selection()
        self._load(data)

    def _load(self, data: Iterable[ListDataDict]) -> None:
        self.ids: Dict[str, int] = {}
        self.columns: Dict[str, Gtk.TreeViewColumn] = {}

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

    def selected(self) -> Optional[Gtk.TreeIter]:
        model, tree_iter = self.selection.get_selected()
        if tree_iter is not None:
            tree_iter = model.convert_iter_to_child_iter(tree_iter)
        return tree_iter

    def delete(self, iterid: Union[Gtk.TreeIter, Gtk.TreePath, int, str]) -> bool:
        if isinstance(iterid, Gtk.TreeIter):
            tree_iter: Optional[Gtk.TreeIter] = iterid
        else:
            tree_iter = self.get_iter(iterid)

        if tree_iter is None:
            return False
        if self.liststore.iter_is_valid(tree_iter):
            self.liststore.remove(tree_iter)
            return True
        else:
            return False

    def _add(self, **columns: object) -> Collection[object]:
        items: Dict[int, object] = {}
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

    def get_conditional(self, **cols: object) -> List[int]:
        ret = []
        matches = 0
        for i in range(len(self.liststore)):
            row = self.get(i)
            for k, v in cols.items():
                if row[k] == v:
                    matches += 1

            if matches == len(cols):
                ret.append(i)

            matches = 0

        return ret

    def set(self, iterid: Union[Gtk.TreeIter, int, str], **cols: object) -> None:
        if isinstance(iterid, Gtk.TreeIter):
            tree_iter: Optional[Gtk.TreeIter] = iterid
        else:
            tree_iter = self.get_iter(iterid)

        if tree_iter is not None:
            for k, v in cols.items():
                self.liststore.set(tree_iter, self.ids[k], v)

    def get(self, iterid: Union[Gtk.TreeIter, Gtk.TreePath, int, str], *items: str) -> Dict[str, Any]:
        ret = {}

        if iterid is not None:
            if isinstance(iterid, Gtk.TreeIter):
                tree_iter: Optional[Gtk.TreeIter] = iterid
            else:
                tree_iter = self.get_iter(iterid)
            assert tree_iter is not None
            if len(items) == 0:
                for k, v in self.ids.items():
                    ret[k] = self.liststore.get(tree_iter, v)[0]
            else:
                for i in range(len(items)):
                    if items[i] in self.ids:
                        ret[items[i]] = self.liststore.get(tree_iter, self.ids[items[i]])[0]
        else:
            return {}

        return ret

    def get_iter(self, path: Optional[Union[Gtk.TreePath, int, str]]) -> Optional[Gtk.TreeIter]:
        if path is None:
            return None

        try:
            return self.liststore.get_iter(path)
        except ValueError:
            return None

    def clear(self) -> None:
        self.liststore.clear()

    def compare(self, iter_a: Optional[Gtk.TreeIter], iter_b: Optional[Gtk.TreeIter]) -> bool:
        if iter_a is not None and iter_b is not None:
            assert self.liststore is not None
            return self.liststore.get_path(iter_a) == self.liststore.get_path(iter_b)
        else:
            return False
