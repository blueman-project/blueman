# coding=utf-8
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


# noinspection PyAttributeOutsideInit
class GenericList(Gtk.TreeView):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.set_name("GenericList")
        self.selection = self.get_selection()
        self._load(data)

    def _load(self, data):
        self.ids = {}
        self.columns = {}

        types = [row["type"] for row in data]

        self.liststore = Gtk.ListStore(*types)
        self.set_model(self.liststore)

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

    def selected(self):
        (model, tree_iter) = self.selection.get_selected()

        return tree_iter

    def delete(self, iterid):
        if type(iterid) == Gtk.TreeIter:
            tree_iter = iterid
        else:
            tree_iter = self.get_iter(iterid)

        if tree_iter is None:
            return False
        if self.liststore.iter_is_valid(tree_iter):
            self.liststore.remove(tree_iter)
            return True
        else:
            return False

    def _add(self, **columns):
        items = {}
        for k, v in self.ids.items():
            items[v] = None

        for k, v in columns.items():
            if k in self.ids:
                items[self.ids[k]] = v
            else:
                raise Exception("Invalid key %s" % k)

        return items.values()

    def append(self, **columns):
        vals = self._add(**columns)
        return self.liststore.append(vals)

    def prepend(self, **columns):
        vals = self._add(**columns)
        return self.liststore.prepend(vals)

    def get_conditional(self, **cols):
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

    def set(self, iterid, **cols):
        if type(iterid) == Gtk.TreeIter:
            tree_iter = iterid
        else:
            tree_iter = self.get_iter(iterid)

        if tree_iter is not None:
            for k, v in cols.items():
                self.liststore.set(tree_iter, self.ids[k], v)
            return True
        else:
            return False

    def get(self, iterid, *items):
        ret = {}

        if iterid is not None:
            if type(iterid) == Gtk.TreeIter:
                tree_iter = iterid
            else:
                tree_iter = self.get_iter(iterid)
            if len(items) == 0:
                for k, v in self.ids.items():
                    ret[k] = self.liststore.get(tree_iter, v)[0]
            else:
                for i in range(len(items)):
                    if items[i] in self.ids:
                        ret[items[i]] = self.liststore.get(tree_iter, self.ids[items[i]])[0]
        else:
            return False

        return ret

    def get_iter(self, path):
        if path is None:
            return None

        try:
            return self.liststore.get_iter(path)
        except ValueError:
            return None

    def clear(self):
        self.liststore.clear()

    def compare(self, iter_a, iter_b):
        if iter_a is not None and iter_b is not None:
            return self.get_model().get_path(iter_a) == self.get_model().get_path(iter_b)
        else:
            return False
