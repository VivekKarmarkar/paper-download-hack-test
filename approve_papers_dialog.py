#!/usr/bin/env python3
"""Approve-papers dialog.

Reads:   identified-papers/identified_and_verified_papers_info.md
Writes:  identified-papers/identified_and_verified_and_validated_papers_info.md

Three top buttons:
  - Approve All        -> copy source verbatim to destination, close.
  - Approve None       -> close, write nothing.
  - Approve Selections -> enable per-row checkboxes + the Submit button.

Bottom Submit button:
  - Only sensitive after "Approve Selections" is clicked.
  - On click, writes only the ticked rows to destination and closes.
"""
import os, sys
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "identified-papers", "identified_and_verified_papers_info.md")
DST = os.path.join(HERE, "identified-papers", "identified_and_verified_and_validated_papers_info.md")


def load_lines():
    if not os.path.exists(SRC):
        return []
    with open(SRC) as f:
        return [ln.rstrip("\n") for ln in f if ln.strip()]


def write_lines(lines):
    with open(DST, "w") as f:
        if lines:
            f.write("\n".join(lines) + "\n")


class ApproveDialog(Gtk.Window):
    def __init__(self, lines):
        super().__init__(title="Approve Papers")
        self.set_default_size(900, 700)
        self.set_border_width(8)
        self.lines = lines
        self.checkbuttons = []
        self.mode = None  # 'all' | 'none' | 'selections'

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.add(outer)

        # ── Top buttons ────────────────────────────────────────────────
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        outer.pack_start(btn_row, False, False, 0)

        btn_all = Gtk.Button(label="Approve All")
        btn_none = Gtk.Button(label="Approve None")
        btn_sel = Gtk.Button(label="Approve Selections")
        btn_all.connect("clicked", self.on_approve_all)
        btn_none.connect("clicked", self.on_approve_none)
        btn_sel.connect("clicked", self.on_approve_selections)
        btn_row.pack_start(btn_all, True, True, 0)
        btn_row.pack_start(btn_none, True, True, 0)
        btn_row.pack_start(btn_sel, True, True, 0)

        # ── Status label ──────────────────────────────────────────────
        self.status = Gtk.Label(label=f"{len(lines)} verified entries — choose an action above.")
        self.status.set_xalign(0)
        outer.pack_start(self.status, False, False, 0)

        # ── Scrollable list of paper rows ─────────────────────────────
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        outer.pack_start(scroller, True, True, 0)

        list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        scroller.add(list_box)

        for ln in lines:
            cb = Gtk.CheckButton(label=ln)
            # wrap long labels
            child = cb.get_child()
            if isinstance(child, Gtk.Label):
                child.set_line_wrap(True)
                child.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
                child.set_xalign(0)
                child.set_max_width_chars(120)
            cb.set_sensitive(False)  # disabled until "Approve Selections" mode
            self.checkbuttons.append(cb)
            list_box.pack_start(cb, False, False, 0)

        # ── Bottom: Submit + Cancel ───────────────────────────────────
        bottom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        outer.pack_start(bottom, False, False, 0)
        bottom.pack_start(Gtk.Box(), True, True, 0)  # spacer
        btn_cancel = Gtk.Button(label="Cancel")
        btn_cancel.connect("clicked", lambda *_: self.close_no_write())
        self.btn_submit = Gtk.Button(label="Submit")
        self.btn_submit.set_sensitive(False)
        self.btn_submit.connect("clicked", self.on_submit)
        bottom.pack_start(btn_cancel, False, False, 0)
        bottom.pack_start(self.btn_submit, False, False, 0)

        self.connect("destroy", lambda *_: Gtk.main_quit())

    # ── Handlers ────────────────────────────────────────────────────
    def on_approve_all(self, *_):
        write_lines(self.lines)
        print(f"[approve-all] wrote {len(self.lines)} entries -> {DST}")
        Gtk.main_quit()

    def on_approve_none(self, *_):
        print("[approve-none] no changes; destination left untouched.")
        Gtk.main_quit()

    def on_approve_selections(self, *_):
        self.mode = "selections"
        for cb in self.checkbuttons:
            cb.set_sensitive(True)
        self.btn_submit.set_sensitive(True)
        self.status.set_text(f"Tick the papers you approve, then click Submit. ({len(self.lines)} candidates)")

    def on_submit(self, *_):
        selected = [ln for cb, ln in zip(self.checkbuttons, self.lines) if cb.get_active()]
        write_lines(selected)
        print(f"[submit] wrote {len(selected)} of {len(self.lines)} entries -> {DST}")
        Gtk.main_quit()

    def close_no_write(self):
        print("[cancel] no changes; destination left untouched.")
        Gtk.main_quit()


def main():
    lines = load_lines()
    if not lines:
        print(f"No entries found in {SRC}. Nothing to approve.")
        sys.exit(0)
    win = ApproveDialog(lines)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
