
$fn = 64;



difference() {
    union() {
        cylinder(d=35, h=2, center=true);

        difference() {
            cylinder(d=52, h=2, center=true);
            translate([0, 0, 0.51]) {
                cylinder(d=50, h=1, center=true);
            }
        }
    }

    cylinder(d=7, h=30, center=true);
    translate([6, 0, 0]) {
        cylinder(d=2.5, h=30, center=true);
    }

    translate([24.5, 0, 0]) {
        cylinder(d=14, h=3, center=true);
    }

}

