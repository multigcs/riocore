
$fn = 32;  


for ( i = [0 : 7] ) {

    translate([i*(2.54*3)+(2.54*3)/2, 0, 0]) {

        difference() {
            union() {  
                cylinder(d=5, h=6);
                cylinder(d=7, h=1.5);
            }
            cylinder(d=4, h=1);
        }
        translate([0, 7, 0.5/2]) {
            cube([2, 8, 0.5], center=true);
        }

        translate([0, 10, 0.5/2]) {
            cube([10, 2, 0.5], center=true);
        }

    }


}



