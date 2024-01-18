

$fn=32;


module disp() {
    translate([0, 20, 1]) {
        cube([76, 50, 2], center=true);
    }

    translate([0, 28.5, 4.5]) {
        cube([63, 15.5, 9], center=true);
    }

    for (i = [0:3]) {
        translate([i*(2.54*3)+(2.54*3)/2, 0, 0]) {
            cylinder(d=4, h=6.3);
        }
        translate([-i*(2.54*3)-(2.54*3)/2, 0, 0]) {
            cylinder(d=4, h=6.3);
        }
    }

    for (i = [0:3]) {
        translate([i*(2.6*3)+(2.6*3)/2, 40.5, 0]) {
            cylinder(d=3, h=6.7);
        }
        translate([-i*(2.6*3)-(2.6*3)/2, 40.5, 0]) {
            cylinder(d=3, h=6.7);
        }
    }

}



difference() {
    
    more = 8;
    
    translate([0, 20, 7.5]) {
        cube([76+more, 50+more, 2], center=true);
    }

    disp();

    off = 0.7;

    translate([68/2, -off , 0]) {
        cylinder(d=3.2, h=26.7);
    }
    translate([-68/2, -off , 0]) {
        cylinder(d=3.2, h=26.7);
    }
    translate([68/2, 40-off , 0]) {
        cylinder(d=3.2, h=26.7);
    }
    translate([-68/2, 40-off , 0]) {
        cylinder(d=3.2, h=26.7);
    }


    for (i = [0:3]) {
        translate([i*(2.54*3)+(2.54*3)/2, 0, 0]) {
            cylinder(d=6, h=16.3);
        }
        translate([-i*(2.54*3)-(2.54*3)/2, 0, 0]) {
            cylinder(d=6, h=16.3);
        }
    }

    for (i = [0:3]) {
        translate([i*(2.6*3)+(2.6*3)/2, 40.5, 0]) {
            cylinder(d=3, h=16.7);
        }
        translate([-i*(2.6*3)-(2.6*3)/2, 40.5, 0]) {
            cylinder(d=3, h=16.7);
        }
    }


}

    names = ["F", "", "X", "Y"];
    cmds = ["Z", "", "<", ">"];

    for (i = [0:3]) {
        color([1,0,0])
        translate([i*(2.54*3)+(2.54*3)/2, 5, 7.8]) {
            scale([0.5, 0.5, 1]) {
                linear_extrude(1.5)
                    text(cmds[i], font="Liberation Sans", halign="center");
            }
        }

        color([1,0,0])
        translate([-i*(2.54*3)-(2.54*3)/2, 5, 7.8]) {
            scale([0.5, 0.5, 1]) {
                linear_extrude(1.5)
                    text(names[3-i], font="Liberation Sans", halign="center");
            }
        }

    }

    names2 = ["P", "", "X", "Y"];
    stats = ["Z", "", "", "S"];

    for (i = [0:3]) {
        color([1,0,0])
        translate([i*(2.6*3)+(2.6*3)/2, 43, 7.8]) {
            scale([0.5, 0.5, 1]) {
                linear_extrude(1.5)
                    text(stats[i], font="Liberation Sans", halign="center");
            }
        }

        color([1,0,0])
        translate([-i*(2.6*3)-(2.6*3)/2, 43, 7.8]) {
            scale([0.5, 0.5, 1]) {
                linear_extrude(1.5)
                    text(names2[3-i], font="Liberation Sans", halign="center");
            }
        }
    }






//disp();






