#!/usr/bin/env python3

# import sys
# import math

from PyQt6.QtCore import pyqtSignal, QSize, Qt, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL import GL
from OpenGL.GL import glColor4f
from OpenGL import GLU

import _thread

import glnav
from rs274 import glcanon
from rs274 import interpret
import linuxcnc
import gcode

import re
import tempfile
import shutil
import os


#################
# Helper class
#################
class DummyProgress:
    def nextphase(self, unused):
        pass

    def progress(self):
        pass


class Progress:
    def __init__(self, phases, total):
        self.num_phases = phases
        self.phase = 0
        self.total = total or 1
        self.lastcount = 0
        self.text = None

    def update(self, count, force=0):
        if force or count - self.lastcount > 400:
            fraction = (self.phase + count * 1.0 / self.total) / self.num_phases
            self.lastcount = count
            self.emit_percent(int(fraction * 100))

    # this is class patched
    def emit_percent(self, percent):
        pass

    def nextphase(self, total):
        self.phase += 1
        self.total = total or 1
        self.lastcount = -100
        self.update(0, True)

    def done(self):
        self.emit_percent(-1)

    # not sure if this is used - copied from AXIS code
    def set_text(self, text):
        if self.text is None:
            self.text = ".info.progress"
        else:
            print(".info.progress", text)


class StatCanon(glcanon.GLCanon, interpret.StatMixin):
    def __init__(self, colors, geometry, is_foam, lathe_view_option, stat, random, text, linecount, progress, arcdivision):
        glcanon.GLCanon.__init__(self, colors, geometry, is_foam)
        interpret.StatMixin.__init__(self, stat, random)
        self.lathe_view_option = lathe_view_option
        self.text = text
        self.linecount = linecount
        self.progress = progress
        self.aborted = False
        self.arcdivision = arcdivision

    def is_lathe(self):
        return self.lathe_view_option

    def change_tool(self, pocket):
        glcanon.GLCanon.change_tool(self, pocket)
        interpret.StatMixin.change_tool(self, pocket)

    def next_line(self, st):
        glcanon.GLCanon.next_line(self, st)
        self.progress.update(self.lineno)
        if self.notify:
            self.output_notify_message(self.notify_message)
            self.notify = 0

    # this is class patched
    # output the text from the magic comment eg: (PREVIEW,notify,The text)
    def output_notify_message(self, message):
        pass


###############################
# widget for graphics plotting
###############################
class emc_plot(QOpenGLWidget, glcanon.GlCanonDraw, glnav.GlNavBase):
    percentLoaded = pyqtSignal(int)
    xRotationChanged = pyqtSignal(int)
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)
    rotation_vectors = [(1.0, 0.0, 0.0), (0.0, 0.0, 1.0)]

    def __init__(self, parent=None):
        super(emc_plot, self).__init__(parent)
        glnav.GlNavBase.__init__(self)

        def C(s):
            a = self.colors[s + "_alpha"]
            s = self.colors[s]
            return [int(x * 255) for x in s + (a,)]

        # requires linuxcnc running before loading this widget
        inifile = os.environ.get("INI_FILE_NAME", "/dev/null")

        stat = linuxcnc.stat()
        stat.poll()

        self.inifile = linuxcnc.ini(inifile)
        self.foam_option = bool(self.inifile.find("DISPLAY", "FOAM"))
        try:
            trajcoordinates = self.inifile.find("TRAJ", "COORDINATES").lower().replace(" ", "")
        except Exception:
            trajcoordinates = "unknown"
        kinsmodule = self.inifile.find("KINS", "KINEMATICS")

        self.logger = linuxcnc.positionlogger(
            linuxcnc.stat(), C("backplotjog"), C("backplottraverse"), C("backplotfeed"), C("backplotarc"), C("backplottoolchange"), C("backplotprobing"), self.get_geometry(), self.foam_option
        )
        # start tracking linuxcnc position so we can plot it
        _thread.start_new_thread(self.logger.start, (0.01,))
        glcanon.GlCanonDraw.__init__(self, stat, self.logger)
        glcanon.GlCanonDraw.init_glcanondraw(self, trajcoordinates=trajcoordinates, kinsmodule=kinsmodule)

        # set defaults
        self.display_loaded = False
        self.current_view = "p"
        self.fingerprint = ()
        self.select_primed = None
        self.lat = 0
        self.minlat = -90
        self.maxlat = 90

        self._current_file = None
        self.gcode_properties = None
        self.highlight_line = None
        self.program_alpha = False
        self.use_joints_mode = True
        self.use_commanded = True

        self.background_color = (0.0, 0.0, 0.0)

        self.enable_dro = True
        self.show_limits = True
        self.show_extents_option = True
        self.show_live_plot = True
        self.show_velocity = True
        self.metric_units = False

        self.show_program = True
        self.show_rapids = True
        self.show_tool = True
        self.show_lathe_radius = False
        self.show_dtg = False
        self.grid_size = 0.0
        self.show_offsets = False
        self.show_overlay = False
        self.use_relative = True

        temp = self.inifile.find("DISPLAY", "LATHE") or "False"
        self.lathe_option = temp.lower() in ["1", "true"]

        self.use_default_controls = True
        self.mouse_btn_mode = 0
        self._mousemoved = False
        self.cancel_rotate = False
        self.use_gradient_background = False
        self.gradient_color1 = (0.0, 0.0, 0.0)
        self.gradient_color2 = (0.0, 0.0, 0.0)
        self.a_axis_wrapped = self.inifile.find("AXIS_A", "WRAPPED_ROTARY")
        self.b_axis_wrapped = self.inifile.find("AXIS_B", "WRAPPED_ROTARY")
        self.c_axis_wrapped = self.inifile.find("AXIS_C", "WRAPPED_ROTARY")

        live_axis_count = 0
        for i, j in enumerate("XYZABCUVW"):
            if self.stat.axis_mask & (1 << i) == 0:
                continue
            live_axis_count += 1
        self.num_joints = int(self.inifile.find("KINS", "JOINTS") or live_axis_count)

        # initialize variables for user view
        self.presetViewSettings(v=None, z=0, x=0, y=0, lat=None, lon=None)
        # allow anyone else to preset user view with better settings
        self._presetFlag = False

        self.object = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

        self.Green = QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        self.inhibit_selection = True

        self.dro_in = "% 9.4f"
        self.dro_mm = "% 9.3f"
        self.dro_deg = "% 9.2f"
        self.dro_vel = "   Vel:% 9.2F"
        self._font = "monospace bold 12"
        self._fontLarge = "monospace bold 22"
        self._largeFontState = False
        self.addTimer()
        self._scroll_mode = 0  # use button list
        self._buttonList = [Qt.MouseButton.LeftButton, Qt.MouseButton.MiddleButton, Qt.MouseButton.RightButton]
        self._invertWheelZoom = False

        # base units of config. updated by subclass (gcode_graphics)
        self.mach_units = "Metric"

    # add a 100ms timer to poll linuxcnc stats
    # this may be overridden in sub widgets
    def addTimer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.poll)
        self.timer.start(100)

    def poll(self):
        s = self.stat
        try:
            s.poll()
        except Exception:
            return
        fingerprint = (
            self.logger.npts,
            self.soft_limits(),
            s.actual_position,
            s.motion_mode,
            s.current_vel,
            s.joint_actual_position,
            s.homed,
            s.limit,
            s.tool_in_spindle,
            s.g5x_offset,
            s.g92_offset,
            s.rotation_xy,
            s.tool_offset,
        )

        if fingerprint[9:12] != self.fingerprint[9:12] or s.file != self._current_file:
            if self.display_loaded:
                self.load()

        if self._current_file != s.file:
            self._current_file = s.file

        if fingerprint != self.fingerprint:
            self.fingerprint = fingerprint
            self.update()
        return True

    # when shown for the first time make sure display is set to the default view
    def showEvent(self, event):
        if not self.display_loaded:
            super(emc_plot, self).showEvent(event)
            self.set_current_view()
            self.display_loaded = True

    def load(self, filename=None):
        s = self.stat
        s.poll()
        if not filename and s.file:
            filename = s.file
        elif not filename and not s.file:
            return

        lines = open(filename).readlines()
        progress = Progress(2, len(lines))
        # monkey patch function to call ours
        progress.emit_percent = self.emit_percent

        code = []
        i = 0
        for i, ll in enumerate(lines):
            ll = ll.expandtabs().replace("\r", "")
            code.extend(["%6d: " % (i + 1), "lineno", ll, ""])
            if i % 1000 == 0:
                del code[:]
                progress.update(i)
        if code:
            pass
        progress.nextphase(len(lines))

        td = tempfile.mkdtemp()
        self._current_file = filename
        try:
            random = int(self.inifile.find("EMCIO", "RANDOM_TOOLCHANGER") or 0)
            arcdivision = int(self.inifile.find("DISPLAY", "ARCDIVISION") or 64)
            text = ""
            canon = StatCanon(self.colors, self.get_geometry(), self.foam_option, self.lathe_option, s, text, random, i, progress, arcdivision)
            # monkey patched function to call ours
            canon.output_notify_message = self.output_notify_message
            parameter = self.inifile.find("RS274NGC", "PARAMETER_FILE")
            temp_parameter = os.path.join(td, os.path.basename(parameter or "linuxcnc.var"))
            if parameter:
                shutil.copy(parameter, temp_parameter)
            canon.parameter_file = temp_parameter
            unitcode = "G%d" % (20 + (s.linear_units == 1))
            initcode = self.inifile.find("RS274NGC", "RS274NGC_STARTUP_CODE") or ""
            result, seq = self.load_preview(filename, canon, unitcode, initcode)
            if result > gcode.MIN_ERROR:
                self.report_gcode_error(result, seq, filename)
            self.logger.set_depth(self.from_internal_linear_unit(self.get_foam_z()), self.from_internal_linear_unit(self.get_foam_w()))
            self.calculate_gcode_properties(canon)
        except Exception:
            self.gcode_properties = None
        finally:
            shutil.rmtree(td)
            if canon:
                canon.progress = DummyProgress()
            try:
                progress.done()
            except UnboundLocalError:
                pass
        self._redraw()

    # monkey patched function from StatCanon class
    def output_notify_message(self, message):
        pass

    # monkey patched function from Progress class
    def emit_percent(self, percent):
        self.percentLoaded.emit(percent)

    def from_internal_linear_unit(self, v, unit=None):
        if unit is None:
            unit = self.stat.linear_units
        lu = (unit or 1) * 25.4
        return v * lu

    def calculate_gcode_properties(self, canon):
        def dist(xxx_todo_changeme, xxx_todo_changeme1):
            (x, y, z) = xxx_todo_changeme
            (p, q, r) = xxx_todo_changeme1
            return ((x - p) ** 2 + (y - q) ** 2 + (z - r) ** 2) ** 0.5

        def from_internal_units(pos, unit=None):
            if unit is None:
                unit = self.stat.linear_units
            lu = (unit or 1) * 25.4

            lus = [lu, lu, lu, 1, 1, 1, lu, lu, lu]
            return [a * b for a, b in zip(pos, lus)]

        props = {}
        loaded_file = self._current_file
        max_speed = float(self.inifile.find("DISPLAY", "MAX_LINEAR_VELOCITY") or self.inifile.find("TRAJ", "MAX_LINEAR_VELOCITY") or self.inifile.find("AXIS_X", "MAX_VELOCITY") or 1)

        if not loaded_file:
            props["name"] = "No file loaded"
        else:
            ext = os.path.splitext(loaded_file)[1]
            program_filter = None
            if ext:
                program_filter = self.inifile.find("FILTER", ext[1:])
            name = os.path.basename(loaded_file)
            if program_filter:
                props["name"] = "generated from %s" % name
            else:
                props["name"] = name

            size = os.stat(loaded_file).st_size
            lines = sum(1 for line in open(loaded_file))
            props["size"] = "%(size)s bytes\n%(lines)s gcode lines" % {"size": size, "lines": lines}

            # report props in gcode's units
            if 200 in canon.state.gcodes:
                units = "in"
                fmt = "%.4f"
                conv = 1 / 25.4
            else:
                units = "mm"
                fmt = "%.3f"
                conv = 1

            mf = max_speed

            g0 = sum(dist(ll[1][:3], ll[2][:3]) for ll in canon.traverse)
            g1 = sum(dist(ll[1][:3], ll[2][:3]) for ll in canon.feed) + sum(dist(ll[1][:3], ll[2][:3]) for ll in canon.arcfeed)
            gt = (
                sum(dist(ll[1][:3], ll[2][:3]) / min(mf, ll[3]) for ll in canon.feed)
                + sum(dist(ll[1][:3], ll[2][:3]) / min(mf, ll[3]) for ll in canon.arcfeed)
                + sum(dist(ll[1][:3], ll[2][:3]) / mf for ll in canon.traverse)
                + canon.dwell_time
            )

            props["g0"] = "%f %s".replace("%f", fmt) % (self.from_internal_linear_unit(g0, conv), units)
            props["g1"] = "%f %s".replace("%f", fmt) % (self.from_internal_linear_unit(g1, conv), units)
            if gt > 120:
                props["run"] = "%.1f Minutes" % (gt / 60)
            else:
                props["run"] = "%d Seconds" % (int(gt))

            props["toollist"] = canon.tool_list

            min_extents = from_internal_units(canon.min_extents, conv)
            max_extents = from_internal_units(canon.max_extents, conv)
            min_extents_zero_rxy = from_internal_units(canon.min_extents_zero_rxy, conv)
            max_extents_zero_rxy = from_internal_units(canon.max_extents_zero_rxy, conv)
            for i, c in enumerate("xyz"):
                a = min_extents[i]
                b = max_extents[i]
                d = min_extents_zero_rxy[i]
                e = max_extents_zero_rxy[i]
                props[c] = "%f to %f = %f %s".replace("%f", fmt) % (a, b, b - a, units)
                props[c + "_zero_rxy"] = "%f to %f = %f %s".replace("%f", fmt) % (d, e, e - d, units)
            props["machine_unit_sys"] = self.mach_units

            props["gcode_units"] = units

        self.gcode_properties = props

    def set_font(self, large=None):
        # set to None to reset the DRO font
        if large is None:
            large = self._largeFontState
        if large:
            font = self._fontLarge
            self._largeFontState = True
        else:
            font = self._font
            self._largeFontState = False
        self.font_base, width, linespace = glnav.use_pango_font(font, 0, 128)
        self.font_linespace = linespace
        self.font_charwidth = width
        self.update()

    # setup details when window shows
    def realize(self):
        self.set_current_view()
        # if user view has not been preset - set it now
        # as it's in a reasonable place
        if not self._presetFlag:
            self.recordCurrentViewSettings()

        s = self.stat
        try:
            s.poll()
        except Exception:
            return
        self._current_file = None
        self.set_font(False)
        glcanon.GlCanonDraw.realize(self)
        if s.file:
            self.load()

    # getter / setters
    def get_font_info(self):
        return self.font_charwidth, self.font_linespace, self.font_base

    def get_program_alpha(self):
        return self.program_alpha

    def get_num_joints(self):
        return self.num_joints

    def get_joints_mode(self):
        return self.use_joints_mode

    def get_show_commanded(self):
        return self.use_commanded

    def get_show_extents(self):
        return self.show_extents_option

    def get_gcode_properties(self):
        return self.gcode_properties

    def get_show_limits(self):
        return self.show_limits

    def get_show_live_plot(self):
        return self.show_live_plot

    def get_show_machine_speed(self):
        return self.show_velocity

    def get_show_metric(self):
        return self.metric_units

    def get_show_program(self):
        return self.show_program

    def get_show_rapids(self):
        return self.show_rapids

    def get_show_relative(self):
        return self.use_relative

    def get_show_tool(self):
        return self.show_tool

    def get_show_distance_to_go(self):
        return self.show_dtg

    def get_grid_size(self):
        return self.grid_size

    def get_show_offsets(self):
        return self.show_offsets

    def get_view(self):
        view_dict = {"x": 0, "y": 1, "y2": 1, "z": 2, "z2": 2, "p": 3}
        return view_dict.get(self.current_view, 3)

    def get_geometry(self):
        temp = self.inifile.find("DISPLAY", "GEOMETRY") or "XYZABCUVW"
        if temp:
            _geometry = re.split(" *(-?[XYZABCUVW])", temp.upper())
            self._geometry = "".join(reversed(_geometry))
        else:
            self._geometry = "XYZABCUVW"
        return self._geometry

    def is_lathe(self):
        return self.lathe_option

    def is_foam(self):
        return self.foam_option

    def get_current_tool(self):
        for i in self.stat.tool_table:
            if i[0] == self.stat.tool_in_spindle:
                return i

    def get_highlight_line(self):
        return self.highlight_line

    def get_a_axis_wrapped(self):
        return self.a_axis_wrapped

    def get_b_axis_wrapped(self):
        return self.b_axis_wrapped

    def get_c_axis_wrapped(self):
        return self.c_axis_wrapped

    def set_current_view(self):
        if self.current_view not in ["p", "x", "y", "y2", "z", "z2"]:
            return
        return getattr(self, "set_view_%s" % self.current_view)()

    def clear_live_plotter(self):
        self.logger.clear()
        self.update()

    def winfo_width(self):
        return self.geometry().width()

    def winfo_height(self):
        return self.geometry().height()

    def activate(self):
        self.makeCurrent()

    def deactivate(self):
        self.doneCurrent()

    def swapbuffers(self):
        self.swapBuffers()

    # redirect for conversion from pygtk to pyqt
    # gcannon assumes this function name
    def _redraw(self):
        self.update()

    # This overrides glcannon.py method so we can change the joint DRO
    # this is turned off because amending extra variables (posstrs and droposstrs)
    # breaks the screen display somehow
    # remove _OFF and re make to enable function
    def joint_dro_format_OFF(self, s, spd, num_of_joints, limit, homed):
        posstrs = ["  %s:% 9.4f" % i for i in zip(list(range(num_of_joints)), s.joint_actual_position)]
        droposstrs = posstrs

        if self.get_show_machine_speed():
            format = "% 6s:" + self.dro_in
            diaformat = " " + format
            if self.metric_units:
                format = "% 6s:" + self.dro_mm
                spd = spd * 25.4
            spd = spd * 60
            # adding this strangely breaks the DRO _after_ homing
            posstrs.append(format % ("Vel", spd))
            droposstrs.append(diaformat % ("Vel", spd))

        return limit, homed, posstrs, droposstrs

    # This overrides glcannon.py method so we can change the DRO
    def dro_format(self, s, spd, dtg, limit, homed, positions, axisdtg, g5x_offset, g92_offset, tlo_offset):
        if self.metric_units:
            format = "% 6s:" + self.dro_mm
            if self.show_dtg:
                droformat = " " + format + "  DTG %1s:" + self.dro_mm
            else:
                droformat = " " + format
            offsetformat = "% 5s %1s:" + self.dro_mm + "  G92 %1s:" + self.dro_mm
            toolformat = "% 5s %1s:" + self.dro_mm
            rotformat = "% 5s %1s:" + self.dro_deg

        else:
            format = "% 6s:" + self.dro_in
            if self.show_dtg:
                droformat = " " + format + "  DTG %1s:" + self.dro_in
            else:
                droformat = " " + format
            offsetformat = "% 5s %1s:" + self.dro_in + "  G92 %1s:" + self.dro_in
            toolformat = "% 5s %1s:" + self.dro_in
            rotformat = "% 5s %1s:" + self.dro_deg
        diaformat = " " + format

        posstrs = []
        droposstrs = []
        for i in range(9):
            if self.is_lathe() and i == 1:
                continue
            a = "XYZABCUVW"[i]
            if s.axis_mask & (1 << i):
                posstrs.append(format % (a, positions[i]))
                if self.show_dtg:
                    droposstrs.append(droformat % (a, positions[i], a, axisdtg[i]))
                else:
                    droposstrs.append(droformat % (a, positions[i]))
        droposstrs.append("")

        for i in range(9):
            if self.is_lathe() and i == 1:
                continue
            index = s.g5x_index
            if index < 7:
                label = "G5%d" % (index + 3)
            else:
                label = "G59.%d" % (index - 6)

            a = "XYZABCUVW"[i]
            if s.axis_mask & (1 << i):
                droposstrs.append(offsetformat % (label, a, g5x_offset[i], a, g92_offset[i]))
        droposstrs.append(rotformat % (label, "R", s.rotation_xy))

        droposstrs.append("")
        for i in range(9):
            if self.is_lathe() and i == 1:
                continue
            a = "XYZABCUVW"[i]
            if s.axis_mask & (1 << i):
                droposstrs.append(toolformat % ("TLO", a, tlo_offset[i]))

        # if its a lathe only show radius or diameter as per property
        if self.is_lathe():
            posstrs[0] = ""
            if self.show_lathe_radius:
                posstrs.insert(1, format % ("Rad", positions[0]))
            else:
                posstrs.insert(1, format % ("Dia", positions[0] * 2.0))
            droposstrs[0] = ""
            if self.show_dtg:
                if self.show_lathe_radius:
                    droposstrs.insert(1, droformat % ("Rad", positions[0], "R", axisdtg[0]))
                else:
                    droposstrs.insert(1, droformat % ("Dia", positions[0] * 2.0, "D", axisdtg[0] * 2.0))
            else:
                if self.show_lathe_radius:
                    droposstrs.insert(1, droformat % ("Rad", positions[0]))
                else:
                    droposstrs.insert(1, diaformat % ("Dia", positions[0] * 2.0))

        if self.show_velocity:
            posstrs.append(self.dro_vel % (spd))
            pos = 0
            for i in range(9):
                if s.axis_mask & (1 << i):
                    pos += 1
            if self.is_lathe:
                pos += 1
            droposstrs.insert(pos, " " + self.dro_vel % (spd))

        if self.show_dtg:
            posstrs.append(format % ("DTG", dtg))

        # show extrajoints (if not showing offsets)
        if s.num_extrajoints > 0 and (not self.get_show_offsets()):
            posstrs.append("Extra Joints:")
            for jno in range(self.get_num_joints() - s.num_extrajoints, self.get_num_joints()):
                jval = s.joint_actual_position[jno]
                jstr = "   EJ%d:% 9.4f" % (jno, jval)
                if jno >= 10:
                    jstr = "  EJ%2d:% 9.4f" % (jno, jval)
                posstrs.append(jstr)

        return limit, homed, posstrs, droposstrs

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(400, 400)

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            self.update()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.update()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.update()

    def setZoom(self, zoom):
        self.distance = zoom / 100.0
        self.update()

    def qglColor(self, color):
        glColor4f(color.redF(), color.greenF(), color.blueF(), color.alphaF())

    # called when widget is completely redrawn
    def initializeGL(self):
        # self.object = self.makeObject()
        self.realize()
        GL.glEnable(GL.GL_CULL_FACE)
        return

    # redraws the screen aprox every 100ms
    def paintGL(self):
        try:
            if self.perspective:
                self.redraw_perspective()
            else:
                self.redraw_ortho()

        except Exception:
            return
            GL.glCallList(self.object)

    # replaces glcanoon function
    def redraw_perspective(self):
        w = self.winfo_width()
        h = self.winfo_height()
        GL.glViewport(0, 0, w, h)  # left corner in pixels
        if self.use_gradient_background:
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glLoadIdentity()  # switch to identity (origin) matrix

            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glPushMatrix()
            GL.glPushMatrix()
            GL.glLoadIdentity()

            GL.glDisable(GL.GL_DEPTH_TEST)
            GL.glBegin(GL.GL_QUADS)
            # //bottom color
            color = self.gradient_color1
            GL.glColor3f(color[0], color[1], color[2])
            GL.glVertex2f(-1.0, -1.0)
            GL.glVertex2f(1.0, -1.0)
            # //top color
            color = self.gradient_color2
            GL.glColor3f(color[0], color[1], color[2])
            GL.glVertex2f(1.0, 1.0)
            GL.glVertex2f(-1.0, 1.0)
            GL.glEnd()
            GL.glEnable(GL.GL_DEPTH_TEST)

            GL.glPopMatrix()
            GL.glPopMatrix()

        else:
            # Clear the background and depth buffer.
            GL.glClearColor(*((self.background_color) + (0,)))

            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(
            self.fovy,  # The vertical Field of View, in radians: the amount of "zoom".
            # Think "camera lens". Usually between 90 (extra wide) and 30 (quite zoomed in)
            float(w) / float(h),  # Aspect Ratio. Notice that 4/3 == 800/600 screen resolution
            self.near,  # near clipping plane. Keep as big as possible, or you'll get precision issues.
            self.far + self.distance,
        )  # Far clipping plane. Keep as little as possible.
        GLU.gluLookAt(
            0,
            0,
            self.distance,  # the position of your camera, in world space
            0,
            0,
            0,  # where you want to look at, in world space
            0.0,
            1.0,
            0.0,
        )  # probably glm::vec3(0,1,0), but (0,-1,0) would make you looking upside-down
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPushMatrix()
        try:
            self.redraw()
        finally:
            GL.glFlush()  # Tidy up
            GL.glPopMatrix()  # Restore the matrix

    # override glcanon function
    def redraw_ortho(self):
        if not self.initialised:
            return
        w = self.winfo_width()
        h = self.winfo_height()
        GL.glViewport(0, 0, w, h)
        if self.use_gradient_background:
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glLoadIdentity()

            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glPushMatrix()
            GL.glPushMatrix()
            GL.glLoadIdentity()

            GL.glDisable(GL.GL_DEPTH_TEST)
            GL.glBegin(GL.GL_QUADS)
            # //bottom color
            color = self.gradient_color1
            GL.glColor3f(color[0], color[1], color[2])
            GL.glVertex2f(-1.0, -1.0)
            GL.glVertex2f(1.0, -1.0)
            # //top color
            color = self.gradient_color2
            GL.glColor3f(color[0], color[1], color[2])
            GL.glVertex2f(1.0, 1.0)
            GL.glVertex2f(-1.0, 1.0)
            GL.glEnd()
            GL.glEnable(GL.GL_DEPTH_TEST)

            GL.glPopMatrix()
            GL.glPopMatrix()

        else:
            GL.glClearColor(*((self.background_color) + (0,)))
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        ztran = self.distance
        k = (abs(ztran or 1)) ** 0.55555
        ll = k * h / w
        GL.glOrtho(-k, k, -ll, ll, -1000, 1000.0)
        GLU.gluLookAt(0, 0, 1, 0, 0, 0, 0.0, 1.0, 0.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPushMatrix()
        try:
            self.redraw()
        finally:
            GL.glFlush()  # Tidy up
            GL.glPopMatrix()  # Restore the matrix

    # override glcanon function
    def basic_lighting(self):
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, (1, -1, 1, 0))
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, self.colors["tool_ambient"] + (0,))
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, self.colors["tool_diffuse"] + (0,))
        GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT, (0.6, 0.6, 0.6, 0))
        GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_DIFFUSE, (1, 1, 1, 0))
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

    # resizes the view to fit the window
    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return
        GL.glViewport((width - side) // 2, (height - side) // 2, side, side)
        GL.glMatrixMode(GL.GL_PROJECTION)  # To operate on projection-view matrix
        GL.glLoadIdentity()  # reset the model-view matrix
        GL.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)  # To operate on model-view matrix

    ####################################
    # Property setting functions
    ####################################
    def set_alpha_mode(self, state):
        self.program_alpha = state
        self.update()

    def set_inhibit_selection(self, state):
        self.inhibit_selection = state

    def get_plot_colors(self):
        return self.logger.get_colors()

    def get_default_plot_colors(self):
        def C(s):
            a = self.colors[s + "_alpha"]
            s = self.colors[s]
            return [int(x * 255) for x in s + (a,)]

        jog = C("backplotjog")
        traverse = C("backplottraverse")
        feed = C("backplotfeed")
        arc = C("backplotarc")
        toolchange = C("backplottoolchange")
        probe = C("backplotprobing")
        return (jog, traverse, feed, arc, toolchange, probe)

    # sets plotter colors to default if arguments left out
    def set_plot_colors(self, jog=None, traverse=None, feed=None, arc=None, toolchange=None, probe=None):
        c = self.logger.get_colors()

        if jog is None:
            jog = c[0]
        if traverse is None:
            traverse = c[1]
        if feed is None:
            feed = c[2]
        if arc is None:
            arc = c[3]
        if toolchange is None:
            toolchange = c[4]
        if probe is None:
            probe = c[5]

        try:
            self.logger.set_colors(jog, traverse, feed, arc, toolchange, probe)
        except Exception:
            pass

    ####################################
    # view controls
    ####################################
    def set_prime(self, x, y):
        if self.select_primed:
            primedx, primedy = self.select_primed
            distance = max(abs(x - primedx), abs(y - primedy))
            if distance > 8:
                self.select_cancel()

    def select_prime(self, x, y):
        self.select_primed = x, y

    # If the hcode program is large the display pauses plotting update
    # while searching. probably needs a thread or compiled code.
    # the actual opengl search is in glcanon.py, GlCanonDraw: select()
    def select_fire(self):
        if self.inhibit_selection:
            return
        if not self.select_primed:
            return
        x, y = self.select_primed
        self.select_primed = None
        self.select(x, y)

    def select_cancel(self, widget=None, event=None):
        self.select_primed = None

    def wheelEvent(self, _event):
        # Use the mouse wheel to zoom in/out
        a = _event.angleDelta().y() / 200
        if a < 0:
            self.zoomin() if self._invertWheelZoom else self.zoomout()
        else:
            self.zoomout() if self._invertWheelZoom else self.zoomin()
        _event.accept()

    def mousePressEvent(self, event):
        self._mousemoved = False
        if event.buttons() & self._buttonList[0]:
            self.select_prime(event.pos().x(), event.pos().y())
            # print self.winfo_width()/2 - event.pos().x(), self.winfo_height()/2 - event.pos().y()
        self.recordMouse(event.pos().x(), event.pos().y())
        self.startZoom(event.pos().y())

    # event.buttons = current button state
    # event_button  = event causing button
    def mouseReleaseEvent(self, event):
        if event.button() & self._buttonList[0]:
            if self._mousemoved is False:
                # only search for the line if we 'clicked'
                # rather then pressed and scrolled
                # select fire starts the search through the gcode
                self.select_fire()

    def mouseDoubleClickEvent(self, event):
        if event.button() & self._buttonList[2]:
            self.logger.clear()

    def mouseMoveEvent(self, event):
        self._mousemoved = True
        if event.buttons():
            b = event.buttons()
            m = self._scroll_mode
            # pan
            if ((b & self._buttonList[0]) and m == 0) or m == 1:
                self.translateOrRotate(event.pos().x(), event.pos().y())
            # rotate
            elif ((b & self._buttonList[2]) and m == 0) or m == 2:
                if not self.cancel_rotate:
                    self.set_prime(event.pos().x(), event.pos().y())
                    self.rotateOrTranslate(event.pos().x(), event.pos().y())
            # zoom
            elif ((b & self._buttonList[1]) and m == 0) or m == 3:
                self.continueZoom(event.pos().y())

    # follow mouse buttons, pan, rotate or zoom on mouse movement
    def setScrollMode(self, mode):
        if mode not in (0, 1, 2, 3):
            mode = 0  # mouse button mode
        self._scroll_mode = mode

    def panView(self, vertical=0, horizontal=0):
        self.translateOrRotate(self.xmouse + vertical, self.ymouse + horizontal)

    def rotateView(self, vertical=0, horizontal=0):
        self.rotateOrTranslate(self.xmouse + vertical, self.ymouse + horizontal)

    def recordCurrentViewSettings(self):
        # set flag that presets are valid
        self._presetFlag = True
        self._recordedView = "p" if self.perspective is True else self.current_view
        self._recordedDist = self.get_zoom_distance()
        self._recordedTransX, self._recordedTransY = self.get_total_translation()
        self._lat, self._lon = self.get_viewangle()

    def getRecordedViewSettings(self):
        return self._recordedView, self._recordedDist, self._recordedTransX, self._recordedTransY, self._lat, self._lon

    def setRecordedView(self):
        getattr(self, "set_view_%s" % self._recordedView)()
        self.set_zoom_distance(self._recordedDist)
        self.panView(self._recordedTransX, self._recordedTransY)
        self.set_viewangle(self._lat, self._lon)

    def getCurrentViewSettings(self):
        # if never been set - set it first
        if not self._presetFlag:
            self.recordCurrentViewSettings()
        return "p" if self.perspective is True else self.current_view, self.get_zoom_distance(), self._recordedTransX, self._recordedTransY, self.get_viewangle()[0], self.get_viewangle()[1]

    def presetViewSettings(self, v, z, x, y, lat=None, lon=None):
        self._recordedView = v
        self._recordedDist = z
        self._recordedTransX = x
        self._recordedTransY = y
        self._lat = lat
        self._lon = lon

    def setView(self, v, z, x, y, lat=None, lon=None):
        getattr(self, "set_view_%s" % v)()
        self.set_zoom_distance(z)
        self.panView(x, y)
        self.set_viewangle(lat, lon)
