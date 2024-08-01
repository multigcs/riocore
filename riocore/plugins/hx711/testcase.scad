
$fn=64;



    translate([90, 0, 0]) {
        cube([38, 38, 1], center=true);
        translate([0, 0, 1]) {
            difference() {
                cube([36, 36, 2], center=true);
                cube([3, 40, 2], center=true);
                cube([40, 3, 2], center=true);
            }
        }
    }




difference() {
    cylinder(d=120, h=7, center=true);


    translate([0, 0, 3]) {
        rotate([0, 90, 45]) {
            cylinder(d=5, h=100);
        }
    }

    translate([0, 0, 1]) {
        cube([36, 36, 6], center=true);
    }


    for ( i = [0 : 5] ){
        rotate([0, 0, 90 * i]) {
            translate([0, 39, 2]) {
                cube([34, 34, 5], center=true);
            }
            translate([0, 39, 0]) {
                cube([34-4, 34-4, 15], center=true);
            }
            translate([21, 0, 3]) {
                cube([8, 3, 5], center=true);
            }
        }
        rotate([0, 0, 90 * i + 45]) {
            hull() {
                translate([0, 55, 0]) {
                    cylinder(d=40, h=12, center=true);
                }
                translate([0, 155, 0]) {
                    cylinder(d=180, h=12, center=true);
                }
            }
        }
    }
}

