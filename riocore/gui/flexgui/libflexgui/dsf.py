# Drill Speed and Feed Calculator

import os
import sys
from math import pi

from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
from libflexgui import utilities

"""
• Feed equals .001" per revolution for every 1/16" of drill diameter, plus or
  minus .001" on the total.

** Metric Feed 0.025 for every 1.5

• Speed equals 80 surface feet per minute in 100 Brinell hardness material and
  the speed should be reduced 10 surface feet per minute for each additional 50
  points Brinell hardness.
• Feed and speed rates should be reduced up to 45-50‰ when drilling holes deeper
  than 4 drill diameters.
• R.P.M. = (3.8197 / Drill Diameter) x S.F.M.
• S.F.M. = 0.2618 x Drill Diameter x R.P.M.
• I.P.M. = I.P.R. (feed) x R.P.M. (speed)
• Machine Time (seconds) = (60 x Feed minus Stroke) / I.P.M.
1 inch is exactly 25.4 MM Therefore 1 meter is about 39.37 IN, or 3.281 FT.
1 foot is 0.3048 meters

A quick rule to follow is you generally want to be 2/3 the SFM and 2-3 Times
the IPR Feed Rate you would run a HSS/Cobalt Drill at.  This can give you good
starting speeds and feeds.

Also, you want to leave 2%-3% of the hole diameter for the reamer
(Example: .1250" Reamer needs to be drilled to .121"-.1225" before Reaming). 
"""


class dsf_calc(QWidget):
    def __init__(self):
        super().__init__()
        self.path = os.path.dirname(os.path.realpath(sys.argv[0]))
        if self.path == "/usr/bin":
            self.lib_path = "/usr/lib/libflexgui"
        else:
            self.lib_path = os.path.join(self.path, "libflexgui")
        loadUi(os.path.join(self.lib_path, "dsf.ui"), self)

        self.units = "Inch"
        self.dsf_units_pb.clicked.connect(self.change_units)
        self.dfs_calculate_pb.clicked.connect(self.calculate)
        self.dsf_feed_lb.setText("")
        self.dsf_drill_lb.setText("")
        self.dsf_ream_lb.setText("")
        self.setup_material()
        self.dfs_diameter_le.setText("")
        self.dfs_surface_speed_le.setText("")

    def check_dia(self):
        if self.dfs_diameter_le.text() == "":
            msg = "Diameter can not be blank"
            print(msg, "Error")
            return False
        if utilities.is_float(self.dfs_diameter_le.text()):
            return float(self.dfs_diameter_le.text())
        msg = "Diameter is not a valid number"
        print(msg, "Error")
        return False

    def check_speed(self):
        if self.dfs_surface_speed_le.text() == "":
            msg = "Surface Speed can not be blank"
            print(msg, "Error")
            return False
        if utilities.is_float(self.dfs_surface_speed_le.text()):
            return float(self.dfs_surface_speed_le.text())
        msg = "Surface Speed is not a valid number"
        print(msg, "Error")
        return False

    def calculate(self):
        dia = self.check_dia()
        if not dia:
            return
        surface_speed = self.check_speed()
        if not surface_speed:
            return

        if self.units == "Inch":
            rpm = (surface_speed * 12) / (pi * dia)
            feed_rev = (dia / 0.0625) * 0.001
            ream_sfm = surface_speed * 0.667
            ream_rpm = (3.8197 / dia) * ream_sfm
            ream_feed = (feed_rev * 2) * ream_rpm

            # do this after setting reaming data
            rpm = rpm * 0.5 if self.dsf_deep_hole_cb.isChecked() else rpm
            feed_rev = feed_rev * 0.5 if self.dsf_deep_hole_cb.isChecked() else feed_rev
            feed = feed_rev * rpm
            tol = 0.001 * rpm

            self.dsf_feed_lb.setText(f'{feed_rev:.3f}" ± 0.001" per revolution')
            self.dsf_drill_lb.setText(f"{rpm:.0f} RPM {feed:.1f} IPM ± {tol:.1f}")
            self.dsf_ream_lb.setText(f"{ream_rpm:.0f} RPM {ream_feed:.1f} IPM")

        elif self.units == "Metric":
            rpm = (surface_speed * 1000) / (pi * (dia))
            feed_rev = (dia / 1.5875) * 0.0254
            feed = feed_rev * rpm
            tol = 0.0254 * rpm
            ream_smm = surface_speed * 0.667
            ream_feed = feed * 2
            ream_rpm = (ream_smm * 1000) / (pi * (dia))
            rpm = rpm * 0.5 if self.dsf_deep_hole_cb.isChecked() else rpm
            feed_rev = feed_rev * 0.5 if self.dsf_deep_hole_cb.isChecked() else feed_rev

            self.dsf_feed_lb.setText(f"{feed_rev:.3f}mm ± 0.025mm per revolution")
            self.dsf_drill_lb.setText(f"{rpm:.0f} RPM {feed:.1f} mm/M ± {tol:.1f}")
            self.dsf_ream_lb.setText(f"{ream_rpm:.0f} RPM {ream_feed:.1f} mm/M")

    def change_units(self):
        if self.units == "Inch":
            self.dsf_units_pb.setText("Metric")
            self.units = "Metric"
            self.dsf_diameter_units_lb.setText("mm")
            self.dsf_speed_units_lb.setText("SMM")
        elif self.units == "Metric":
            self.dsf_units_pb.setText("Inch")
            self.units = "Inch"
            self.dsf_diameter_units_lb.setText("in")
            self.dsf_speed_units_lb.setText("SFM")
        self.setup_material()

    def setup_material(self):
        self.dsf_material_cb.clear()
        self.dsf_material_cb.addItem("Select")
        sfm = [
            "Aluminum: 200-300 SFM",
            "Brass and Bronze: 150-300 SFM",
            "Bronze (High Tensile) 70-150 SFM",
            "Cast Iron: 60-80 SFM",
            "Plastics: 100-300 SFM",
            "Steel .2 to .3 carbon: 80-110 SFM",
            "Steel .4 to .5 carbon: 70-80 SFM",
            "Tool Steel 1.2 carbon: 50-60 SFM",
            "Stainless Steel: 75-125 SFM",
        ]
        smm = [
            "Aluminum: 60-90 SMM",
            "Brass and Bronze: 45-90 SMM",
            "Bronze (High Tensile) 21-45 SMM",
            "Cast Iron: 18-24 SMM",
            "Plastics: 30-90 SMM",
            "Steel .2 to .3 carbon:  25-34 SMM",
            "Steel .4 to .5 carbon:  21-25 SMM",
            "Tool Steel 1.2 carbon:  15-18 SMM",
            "Stainless Steel: 23-40 SFM",
        ]

        if self.units == "Inch":
            self.dsf_material_cb.addItems(sfm)
        else:
            self.dsf_material_cb.addItems(smm)
