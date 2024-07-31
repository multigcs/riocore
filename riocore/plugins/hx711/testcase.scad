






difference() {
    cube([34+4, 34+4, 10], center=true);

    translate([0, 0, 4]) {
        cube([34, 34, 2.5], center=true);
    }

    translate([0, 0, 0]) {
        cube([34-4, 34-4, 12], center=true);
    }

}




