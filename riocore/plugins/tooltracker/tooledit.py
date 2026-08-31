#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tooledit_qt5.py -- a PyQt5 version of the LinuxCNC 'tooledit' widget.

Features
    * reads / writes a standard LinuxCNC tool table (tool.tbl)
      T# P# X Y Z A B C U V W D I J Q ;comment
    * numeric validation per column, sortable, checkbox column for delete
    * mill / lathe column sets (hide_columns())
    * asks LinuxCNC to re-read the table after saving (if linuxcnc is running)
    * can handle tooltracker entry's

Stand-alone use
    ./tooledit_qt5.py                       # uses $INI_FILE_NAME
    ./tooledit_qt5.py /path/to/tool.tbl
    ./tooledit_qt5.py /path/to/machine.ini  # picks up [EMCIO]TOOL_TABLE
    ./tooledit_qt5.py --lathe tool.tbl

Embedded use
    from tooledit_qt5 import ToolEdit
    te = ToolEdit('/path/to/tool.tbl')
    te.hide_columns('sabcuvwij')     # hide select + unused axes
    layout.addWidget(te)
"""

import os
import re
import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDoubleValidator, QFont, QIntValidator, QKeySequence, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QAbstractItemView, QAction, QApplication, QCheckBox, QFileDialog, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QShortcut, QStyledItemDelegate, QTableView, QVBoxLayout, QWidget

try:
    import linuxcnc
except ImportError:  # allow use off-machine
    linuxcnc = None


# --------------------------------------------------------------------------
#  table description
# --------------------------------------------------------------------------
#  key '#' is the comment column (can't use 'c', that is the C axis)
COLUMNS = (
    # key   header      type
    ("s", "", "check"),
    ("t", "Tool", "int"),
    ("p", "Poc", "int"),
    ("x", "X", "float"),
    ("y", "Y", "float"),
    ("z", "Z", "float"),
    ("a", "A", "float"),
    ("b", "B", "float"),
    ("c", "C", "float"),
    ("u", "U", "float"),
    ("v", "V", "float"),
    ("w", "W", "float"),
    ("d", "Diam", "float"),
    ("i", "Front", "float"),
    ("j", "Back", "float"),
    ("q", "Orient", "int"),
    ("ti", "Timer", "int"),
    ("tw", "Warn", "int"),
    ("tc", "Crit", "int"),
    ("ts", "Sister", "int"),
    ("#", "Comment", "str"),
)

KEYS = [c[0] for c in COLUMNS]
COL = {c[0]: i for i, c in enumerate(COLUMNS)}
TYPE = {c[0]: c[2] for c in COLUMNS}
DATA_KEYS = [k for k in KEYS if k != "s"]
AXIS_KEYS = ("x", "y", "z", "a", "b", "c", "u", "v", "w")

LATHE_HIDE = "yabcuvw"  # columns hidden in lathe mode
MILL_HIDE = "ijq"  # columns hidden in mill mode

TOKEN_RE = re.compile(r"([a-zA-Z])\s*([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)")


def default_record():
    rec = {}
    for k in DATA_KEYS:
        if TYPE[k] == "int":
            rec[k] = 0
        elif TYPE[k] == "float":
            rec[k] = 0.0
        else:
            rec[k] = ""
    return rec


def parse_line(line):
    """Parse one tool table line -> dict, or None if it is not a tool line."""
    line = line.strip()
    if not line or line.startswith(";"):
        return None
    comment = ""
    if ";" in line:
        line, comment = line.split(";", 1)
        comment = comment.strip()
    rec = default_record()
    # tooltracker
    res = re.findall("TT:[0-9]+/[0-9]+/[0-9]+/[0-9]+", comment, re.IGNORECASE)
    if res:
        timer, warning, critical, sister = res[0][3:].split("/")
        comment = comment.replace(res[0], "").strip()
        rec["ti"] = int(timer)
        rec["tw"] = int(warning)
        rec["tc"] = int(critical)
        rec["ts"] = int(sister)
    rec["#"] = comment
    got_tool = False
    for letter, value in TOKEN_RE.findall(line):
        key = letter.lower()
        if key not in DATA_KEYS:
            continue
        try:
            if TYPE[key] == "int":
                rec[key] = int(float(value))
            else:
                rec[key] = float(value)
        except ValueError:
            continue
        if key == "t":
            got_tool = True
    return rec if got_tool else None


def _fmt(value):
    txt = "%.6f" % float(value)
    txt = txt.rstrip("0").rstrip(".")
    return txt if txt not in ("", "-") else "0"


def record_to_line(rec, lathe=False, write_zeros=False):
    parts = ["T%d" % rec["t"], "P%d" % rec["p"]]
    for k in (*AXIS_KEYS, "d"):
        if rec[k] or write_zeros:
            parts.append("%s%s" % (k.upper(), _fmt(rec[k])))
    for k in ("i", "j"):
        if rec[k] or write_zeros or lathe:
            parts.append("%s%s" % (k.upper(), _fmt(rec[k])))
    if rec["q"] or write_zeros or lathe:
        parts.append("Q%d" % rec["q"])
    line = " ".join(parts)
    if rec["#"]:
        line += " ;" + rec["#"].strip()
        line += f" TT:{rec['ti']}/{rec['tw']}/{rec['tc']}/{rec['ts']}"
    return line


# --------------------------------------------------------------------------
#  delegates
# --------------------------------------------------------------------------
class NumberDelegate(QStyledItemDelegate):
    def __init__(self, decimals=4, integer=False, minimum=-99999.0, maximum=99999.0, parent=None):
        super().__init__(parent)
        self.decimals = decimals
        self.integer = integer
        self.minimum = minimum
        self.maximum = maximum

    def displayText(self, value, locale):
        try:
            if self.integer:
                return str(int(value))
            return "{0:.{1}f}".format(float(value), self.decimals)
        except (TypeError, ValueError):
            return str(value)

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if self.integer:
            editor.setValidator(QIntValidator(int(self.minimum), int(self.maximum), editor))
        else:
            val = QDoubleValidator(self.minimum, self.maximum, self.decimals, editor)
            val.setNotation(QDoubleValidator.StandardNotation)
            editor.setValidator(val)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setText(self.displayText(value, None))
        editor.selectAll()

    def setModelData(self, editor, model, index):
        text = editor.text().strip().replace(",", ".")
        try:
            value = int(float(text)) if self.integer else float(text)
        except ValueError:
            value = 0 if self.integer else 0.0
        model.setData(index, value, Qt.EditRole)


class CommentDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setMaxLength(120)
        return editor

    def setModelData(self, editor, model, index):
        # ';' would break the tool table format
        model.setData(index, editor.text().replace(";", " ").strip(), Qt.EditRole)


# --------------------------------------------------------------------------
#  the widget
# --------------------------------------------------------------------------
class ToolEdit(QWidget):
    tableLoaded = pyqtSignal(str)
    tableSaved = pyqtSignal(str)
    dirtyChanged = pyqtSignal(bool)

    def __init__(self, filename=None, lathe=False, parent=None):
        super().__init__(parent)
        self.filename = None
        self.lathe = lathe
        self._dirty = False
        self._loading = False
        self.decimals = 4
        self.write_zeros = False

        self._build_ui()
        self.set_lathe_mode(lathe)
        if filename:
            self.load_file(filename)

    # ---------------------------------------------------------------- ui
    def _build_ui(self):
        self.model = QStandardItemModel(0, len(COLUMNS), self)
        for key, header, _t in COLUMNS:
            self.model.setHorizontalHeaderItem(COL[key], QStandardItem(header))
        self.model.itemChanged.connect(self._item_changed)

        self.view = QTableView(self)
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.view.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed | QAbstractItemView.AnyKeyPressed)
        self.view.setSortingEnabled(True)
        self.view.setAlternatingRowColors(True)
        self.view.verticalHeader().setVisible(False)
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.setColumnWidth(COL["s"], 28)

        # delegates
        int_del = NumberDelegate(integer=True, minimum=0, maximum=99999, parent=self)
        for key in ("t", "p"):
            self.view.setItemDelegateForColumn(COL[key], int_del)
        self.view.setItemDelegateForColumn(COL["q"], NumberDelegate(integer=True, minimum=0, maximum=9, parent=self))
        num_del = NumberDelegate(decimals=self.decimals, parent=self)
        for key in (*AXIS_KEYS, "d", "i", "j"):
            self.view.setItemDelegateForColumn(COL[key], num_del)
        self.view.setItemDelegateForColumn(COL["#"], CommentDelegate(self))

        # buttons
        self.btn_add = QPushButton("Add Tool")
        self.btn_del = QPushButton("Delete")
        self.btn_reread = QPushButton("Reread")
        if linuxcnc is not None:
            self.btn_reload = QPushButton("Reload")
        self.btn_save = QPushButton("Save")
        self.btn_saveas = QPushButton("Save As…")
        self.chk_all = QCheckBox("select all")

        self.btn_add.clicked.connect(self.add_tool)
        self.btn_del.clicked.connect(self.delete_tools)
        self.btn_reread.clicked.connect(lambda: self.load_file(self.filename))
        if linuxcnc is not None:
            self.btn_reload.clicked.connect(self.reload_linuxcnc)
        self.btn_save.clicked.connect(lambda: self.save())
        self.btn_saveas.clicked.connect(self.save_as)
        self.chk_all.toggled.connect(self.check_all)

        btns = QHBoxLayout()
        for w in (self.btn_add, self.btn_del, self.chk_all):
            btns.addWidget(w)
        btns.addStretch(1)
        if linuxcnc is not None:
            btns.addWidget(self.btn_reload)
        for w in (self.btn_reread, self.btn_save, self.btn_saveas):
            btns.addWidget(w)

        self.lbl_file = QLabel("no file")
        f = QFont(self.lbl_file.font())
        f.setPointSizeF(max(7.0, f.pointSizeF() - 1))
        self.lbl_file.setFont(f)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.addWidget(self.view)
        lay.addLayout(btns)
        lay.addWidget(self.lbl_file)

        QShortcut(QKeySequence.Save, self, activated=lambda: self.save())
        QShortcut(QKeySequence.New, self, activated=self.add_tool)
        QShortcut(QKeySequence.Delete, self, activated=self.delete_tools)

    # ------------------------------------------------------------ helpers
    def _item_changed(self, item):
        if self._loading:
            return
        if item.column() == COL["s"]:  # checkbox only -> not a change
            return
        self.set_dirty(True)

    def set_dirty(self, state=True):
        if state != self._dirty:
            self._dirty = state
            self._update_caption()
            self.dirtyChanged.emit(state)

    def is_dirty(self):
        return self._dirty

    def _update_caption(self):
        name = self.filename or "(no file)"
        self.lbl_file.setText(("*" if self._dirty else "") + name)

    def _new_item(self, key, value):
        item = QStandardItem()
        item.setEditable(True)
        if key == "s":
            item.setCheckable(True)
            item.setEditable(False)
            item.setSelectable(False)
        elif TYPE[key] == "str":
            item.setData(value, Qt.EditRole)
        else:
            item.setData(value, Qt.EditRole)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return item

    def append_record(self, rec):
        row = [self._new_item("s", None)]
        for key in DATA_KEYS:
            row.append(self._new_item(key, rec[key]))
        self.model.appendRow(row)

    # ------------------------------------------------------------- public
    def load_file(self, filename):
        """Load a tool table (.tbl) or an ini file."""
        if not filename:
            return False
        if filename.lower().endswith(".ini"):
            filename = tool_table_from_ini(filename) or filename
        self._loading = True
        self.model.removeRows(0, self.model.rowCount())
        count, errors = 0, 0
        try:
            with open(filename, "r") as fh:
                for line in fh:
                    rec = parse_line(line)
                    if rec is None:
                        if line.strip():
                            errors += 1
                        continue
                    self.append_record(rec)
                    count += 1
        except IOError as err:
            self._loading = False
            QMessageBox.warning(self, "Tool table", "Could not read %s\n%s" % (filename, err))
            return False
        self._loading = False
        self.filename = filename
        self.set_dirty(False)
        self._update_caption()
        self.view.sortByColumn(COL["t"], Qt.AscendingOrder)
        self.view.resizeColumnsToContents()
        self.view.setColumnWidth(COL["s"], 28)
        self.tableLoaded.emit(filename)
        return True

    def get_records(self):
        recs = []
        for row in range(self.model.rowCount()):
            rec = default_record()
            for key in DATA_KEYS:
                value = self.model.item(row, COL[key]).data(Qt.EditRole)
                if TYPE[key] == "int":
                    rec[key] = int(value or 0)
                elif TYPE[key] == "float":
                    rec[key] = float(value or 0.0)
                else:
                    rec[key] = str(value or "")
            recs.append(rec)
        return recs

    def set_records(self, records):
        self._loading = True
        self.model.removeRows(0, self.model.rowCount())
        for rec in records:
            full = default_record()
            full.update({k: v for k, v in rec.items() if k in full})
            self.append_record(full)
        self._loading = False
        self.set_dirty(True)

    def add_tool(self):
        recs = self.get_records()
        used_t = {r["t"] for r in recs}
        used_p = {r["p"] for r in recs}
        rec = default_record()
        rec["t"] = next(n for n in range(1, 100000) if n not in used_t)
        rec["p"] = next(n for n in range(1, 100000) if n not in used_p)
        self.append_record(rec)
        self.set_dirty(True)
        idx = self.model.index(self.model.rowCount() - 1, COL["t"])
        self.view.scrollTo(idx)
        self.view.setCurrentIndex(idx)

    def checked_rows(self):
        return [r for r in range(self.model.rowCount()) if self.model.item(r, COL["s"]).checkState() == Qt.Checked]

    def check_all(self, state):
        for row in range(self.model.rowCount()):
            self.model.item(row, COL["s"]).setCheckState(Qt.Checked if state else Qt.Unchecked)

    def delete_tools(self):
        rows = self.checked_rows()
        if not rows:
            rows = sorted({i.row() for i in self.view.selectionModel().selectedIndexes()})
        if not rows:
            QMessageBox.information(self, "Delete", "Check the tools you want to delete.")
            return
        tools = ", ".join(str(self.model.item(r, COL["t"]).data(Qt.EditRole)) for r in rows)
        if QMessageBox.question(self, "Delete tools", "Delete tool(s) %s ?" % tools, QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        for row in sorted(rows, reverse=True):
            self.model.removeRow(row)
        self.chk_all.setChecked(False)
        self.set_dirty(True)

    def save(self, filename=None):
        filename = filename or self.filename
        if not filename:
            return self.save_as()
        recs = self.get_records()

        # sanity checks -------------------------------------------------
        tools = [r["t"] for r in recs]
        dupes = {t for t in tools if tools.count(t) > 1}
        if 0 in tools:
            QMessageBox.warning(self, "Tool table", "Tool number 0 is not allowed.")
            return False
        if dupes:
            QMessageBox.warning(self, "Tool table", "Duplicate tool number(s): %s" % ", ".join(str(d) for d in sorted(dupes)))
            return False
        pockets = [r["p"] for r in recs]
        dupes = {p for p in pockets if pockets.count(p) > 1}
        if dupes and QMessageBox.question(self, "Tool table", "Duplicate pocket(s): %s\nSave anyway?" % ", ".join(str(d) for d in sorted(dupes)), QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return False

        recs.sort(key=lambda r: r["t"])
        tmp = filename + ".tmp"
        try:
            with open(tmp, "w") as fh:
                for rec in recs:
                    fh.write(record_to_line(rec, self.lathe, self.write_zeros) + "\n")
            os.replace(tmp, filename)
        except (IOError, OSError) as err:
            QMessageBox.critical(self, "Tool table", "Could not write %s\n%s" % (filename, err))
            return False

        self.filename = filename
        self.set_dirty(False)
        self._update_caption()
        self.reload_linuxcnc()
        self.tableSaved.emit(filename)
        return True

    def save_as(self):
        start = self.filename or os.path.expanduser("~/tool.tbl")
        name, _ = QFileDialog.getSaveFileName(self, "Save tool table", start, "Tool tables (*.tbl);;All (*)")
        if not name:
            return False
        return self.save(name)

    # ------------------------------------------------------ column layout
    def hide_columns(self, keys):
        """keys: string of column letters to hide, e.g. 'sabcuvwij'
        ('#' is the comment column).
        """
        keys = keys.lower()
        for key in KEYS:
            self.view.setColumnHidden(COL[key], key in keys)

    def show_columns(self, keys):
        keys = keys.lower()
        for key in KEYS:
            self.view.setColumnHidden(COL[key], key not in keys)

    def set_lathe_mode(self, state):
        self.lathe = bool(state)
        self.hide_columns(LATHE_HIDE if state else MILL_HIDE)

    def set_decimals(self, decimals):
        self.decimals = decimals
        num_del = NumberDelegate(decimals=decimals, parent=self)
        for key in (*AXIS_KEYS, "d", "i", "j"):
            self.view.setItemDelegateForColumn(COL[key], num_del)
        self.view.viewport().update()

    # ---------------------------------------------------------- linuxcnc
    @staticmethod
    def reload_linuxcnc():
        """Tell a running LinuxCNC to re-read the tool table."""
        if linuxcnc is None:
            return
        try:
            stat = linuxcnc.stat()
            stat.poll()
            cmd = linuxcnc.command()
            cmd.load_tool_table()
        except Exception:
            pass  # LinuxCNC not running -> nothing to do


# --------------------------------------------------------------------------
#  ini helper
# --------------------------------------------------------------------------
def tool_table_from_ini(inifile):
    """Return the absolute path of [EMCIO]TOOL_TABLE of an ini file."""
    if not inifile or not os.path.exists(inifile):
        return None
    table = None
    if linuxcnc is not None:
        try:
            table = linuxcnc.ini(inifile).find("EMCIO", "TOOL_TABLE")
        except Exception:
            table = None
    if not table:  # crude fallback parser
        section = ""
        with open(inifile) as fh:
            for _line in fh:
                line = _line.split("#")[0].strip()
                if line.startswith("["):
                    section = line.strip("[]").upper()
                elif section == "EMCIO" and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip().upper() == "TOOL_TABLE":
                        table = v.strip()
                        break
    if not table:
        return None
    if not os.path.isabs(table):
        table = os.path.join(os.path.dirname(os.path.abspath(inifile)), table)
    return table


# --------------------------------------------------------------------------
#  stand-alone application
# --------------------------------------------------------------------------
class ToolEditWindow(QMainWindow):
    def __init__(self, filename=None, lathe=False):
        super().__init__()
        self.editor = ToolEdit(filename, lathe, self)
        self.setCentralWidget(self.editor)
        self.setWindowTitle("LinuxCNC Tool Editor")
        self.resize(1000, 480)

        m = self.menuBar().addMenu("&File")
        act = QAction("&Open…", self, shortcut=QKeySequence.Open, triggered=self.open_file)
        m.addAction(act)
        m.addAction(QAction("&Save", self, shortcut=QKeySequence.Save, triggered=lambda: self.editor.save()))
        m.addAction(QAction("Save &As…", self, triggered=self.editor.save_as))
        m.addSeparator()
        m.addAction(QAction("&Quit", self, shortcut=QKeySequence.Quit, triggered=self.close))

        v = self.menuBar().addMenu("&View")
        self.act_lathe = QAction("Lathe columns", self, checkable=True, checked=lathe)
        self.act_lathe.toggled.connect(self.editor.set_lathe_mode)
        v.addAction(self.act_lathe)

        self.editor.dirtyChanged.connect(self._title)
        self.editor.tableLoaded.connect(lambda f: self._title())
        self._title()

    def _title(self, *args):
        name = self.editor.filename or "(no file)"
        self.setWindowTitle("%sTool Editor - %s" % ("*" if self.editor.is_dirty() else "", name))

    def open_file(self):
        name, _ = QFileDialog.getOpenFileName(self, "Open tool table", self.editor.filename or os.getcwd(), "Tool tables (*.tbl);;INI files (*.ini);;All files (*)")
        if name:
            self.editor.load_file(name)

    def closeEvent(self, event):
        if self.editor.is_dirty():
            ans = QMessageBox.question(self, "Tool table", "Save changes before closing?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            if ans == QMessageBox.Cancel:
                event.ignore()
                return
            if ans == QMessageBox.Yes and not self.editor.save():
                event.ignore()
                return
        event.accept()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    lathe = "--lathe" in sys.argv or "-l" in sys.argv

    filename = args[0] if args else os.environ.get("INI_FILE_NAME")
    if filename and filename.lower().endswith(".ini"):
        filename = tool_table_from_ini(filename)

    app = QApplication(sys.argv)
    win = ToolEditWindow(filename, lathe)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
