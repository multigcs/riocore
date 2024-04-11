
$fn=32;

/*


hull() {
        translate([-(54.4 + 81)/2, 0, 0]) {
            translate([-54.4/2, 83.5/2, 0]) {
                cylinder(d=6, h=2);
            }
        }
        translate([(54.4 + 81)/2, 0, 0]) {
            translate([54.4/2, 83.5/2, 0]) {
                cylinder(d=6, h=2);
            }
        }
}
hull() {
        translate([-(54.4 + 81)/2, 0, 0]) {
            translate([-54.4/2, -83.5/2, 0]) {
                cylinder(d=6, h=2);
            }
        }
        translate([(54.4 + 81)/2, 0, 0]) {
            translate([54.4/2, -83.5/2, 0]) {
                cylinder(d=6, h=2);
            }
        }
}

hull() {
        translate([-(54.4 + 81)/2, 0, 0]) {
            translate([-54.4/2, -83.5/2, 0]) {
                cylinder(d=6, h=2);
            }
            translate([-54.4/2, 83.5/2, 0]) {
                cylinder(d=6, h=2);
            }
        }
}
hull() {
        translate([(54.4 + 81)/2, 0, 0]) {
            translate([54.4/2, 83.5/2, 0]) {
                cylinder(d=6, h=2);
            }
            translate([54.4/2, -83.5/2, 0]) {
                cylinder(d=6, h=2);
            }
        }
}


translate([-(54.4 + 81)/2, 0, 0]) {
    difference() {
        union() {
            translate([54.4/2, 83.5/2, 0]) {
                cylinder(d=6, h=15);
            }
            translate([-54.4/2, 83.5/2, 0]) {
                cylinder(d=6, h=15);
            }
            translate([54.4/2, -83.5/2, 0]) {
                cylinder(d=6, h=15);
            }
            translate([-54.4/2, -83.5/2, 0]) {
                cylinder(d=6, h=15);
            }
        }
        translate([54.4/2, 83.5/2, 0]) {
            cylinder(d=3, h=16);
        }
        translate([-54.4/2, 83.5/2, 0]) {
            cylinder(d=3, h=16);
        }
        translate([54.4/2, -83.5/2, 0]) {
            cylinder(d=3, h=16);
        }
        translate([-54.4/2, -83.5/2, 0]) {
            cylinder(d=3, h=16);
        }
    }
}

translate([(54.4 + 81)/2, 0, 0]) {
    difference() {
        union() {
            translate([54.4/2, 83.5/2, 0]) {
                cylinder(d=6, h=15);
            }
            translate([-54.4/2, 83.5/2, 0]) {
                cylinder(d=6, h=15);
            }
            translate([54.4/2, -83.5/2, 0]) {
                cylinder(d=6, h=15);
            }
            translate([-54.4/2, -83.5/2, 0]) {
                cylinder(d=6, h=15);
            }
        }
        translate([54.4/2, 83.5/2, 0]) {
            cylinder(d=3, h=16);
        }
        translate([-54.4/2, 83.5/2, 0]) {
            cylinder(d=3, h=16);
        }
        translate([54.4/2, -83.5/2, 0]) {
            cylinder(d=3, h=16);
        }
        translate([-54.4/2, -83.5/2, 0]) {
            cylinder(d=3, h=16);
        }
    }
}

*/

translate([0, 0, 18]) {

difference() {
    union() {
        hull() {
            translate([-(54.4 + 81)/2, 0, 13]) {
                translate([54.4/2, 83.5/2, 0]) {
                    cylinder(d=6, h=2);
                }
            }
            translate([(54.4 + 81)/2, 0, 13]) {
                translate([-54.4/2, 83.5/2, 0]) {
                    cylinder(d=6, h=2);
                }
            }
            translate([-(54.4 + 81)/2, 0, 13]) {
                translate([54.4/2, -83.5/2, 0]) {
                    cylinder(d=6, h=2);
                }
            }
            translate([(54.4 + 81)/2, 0, 13]) {
                translate([-54.4/2, -83.5/2, 0]) {
                    cylinder(d=6, h=2);
                }
            }
        }


        translate([-(54.4 + 81)/2, 0, 0]) {
            translate([54.4/2, 83.5/2, 0]) {
                cylinder(d=6, h=14);
            }
        }
        translate([(54.4 + 81)/2, 0, 0]) {
            translate([-54.4/2, 83.5/2, 0]) {
                cylinder(d=6, h=14);
            }
        }
        translate([-(54.4 + 81)/2, 0, 0]) {
            translate([54.4/2, -83.5/2, 0]) {
                cylinder(d=6, h=14);
            }
        }
        translate([(54.4 + 81)/2, 0, 0]) {
            translate([-54.4/2, -83.5/2, 0]) {
                cylinder(d=6, h=14);
            }
        }
    }

        translate([-(54.4 + 81)/2, 0, 0]) {
            translate([54.4/2, 83.5/2, 0]) {
                cylinder(d=4, h=18);
            }
        }
        translate([(54.4 + 81)/2, 0, 0]) {
            translate([-54.4/2, 83.5/2, 0]) {
                cylinder(d=4, h=18);
            }
        }
        translate([-(54.4 + 81)/2, 0, 0]) {
            translate([54.4/2, -83.5/2, 0]) {
                cylinder(d=4, h=18);
            }
        }
        translate([(54.4 + 81)/2, 0, 0]) {
            translate([-54.4/2, -83.5/2, 0]) {
                cylinder(d=4, h=18);
            }
        }

        translate([0, -5, 10]) {
            cube([20, 50, 15], center=true);
        }

        translate([0, 36, 10]) {
            cube([13, 20, 15], center=true);
        }

        translate([-40.5+7.75, -45, 10]) {
            cube([16.5, 25, 15]);
        }

    }


 
}



