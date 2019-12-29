// Visibility flags
showBoard        = 0;
showBattery      = 0;
showServo        = 0;
showboardIR      = 0;

// Board
board_xyz        = [66.0, 58.0, 1.2];
board_offs       = [-board_xyz[0]/2, -board_xyz[1]/2, 0];
board_rot        = [0, 0, 0];
board_z_angle    = 180;

// Battery
battery_xyz      = [38, 60, 4];
battery_offst    = [-24.5, -40, -0.5];
battery_rot      = [0, 0, 90];

// Servo
servo_xyz        = [20, 19, 8];
servo_xyz2       = [28, 1, 8];
servo_rot        = [0, 0, 0];
servo_offs       = [-45, 5, 0];
servo_offs2      = [-(servo_xyz2[0] -servo_xyz[0])/2, 2, 0];

// Base
base_r           = sqrt(pow(board_xyz[0], 2) +pow(board_xyz[1], 2)) /2;
base_scale       = [1.3, 0.8, 1]; // [1.1, 0.9, 1];
base_dz          = 1.5;

post_dz          = 9; //10.0;
post_wall_d      = 1.0;
doPosts          = 0;

board_holes_xyd  =[[2.5, board_xyz[1] -2, 3],
                   [board_xyz[0] -2, board_xyz[1] -2, 3],
                   [14.5, 2, 3],
                   [42.5, 2, 3]];
                   
base_gaps_hulls  = [/*[-5,                   (board_xyz[1]/2 -3), 
                      (board_xyz[0]/2 -18),  (board_xyz[1]/2 -3), 
                     -5,                    -(board_xyz[1]/2 -6),
                      (board_xyz[0]/2 -18), -(board_xyz[1]/2 -6), 3, 20],
                    */ 
                    /*[-(board_xyz[0]/2 -5), (board_xyz[1]/2 -5), 
                     -19,                    (board_xyz[1]/2 -5), 
                     -(board_xyz[0]/2 -5),  -(board_xyz[1]/2 -6),
                     -19,                   -(board_xyz[1]/2 -6), 3, 20],                     
                    */ 
                    // hole for motor connector
                  /*[ 27,                    (board_xyz[1]/2 -5), 
                      (board_xyz[0]/2 +0),   (board_xyz[1]/2 -5), 
                      27,                    (board_xyz[1]/2 -17),
                      (board_xyz[0]/2 +0),   (board_xyz[1]/2 -17), 1, 20],*/
                    
                    [ -27,                   -(board_xyz[1]/2 -5), 
                      -(board_xyz[0]/2 +0),  -(board_xyz[1]/2 -5), 
                      -27,                   -(board_xyz[1]/2 -17),
                      -(board_xyz[0]/2 +0),  -(board_xyz[1]/2 -17), 1, 20],                      
                    
                    [ 24,                    (board_xyz[1]/2 -53), 
                      (board_xyz[0]/2 -19),  (board_xyz[1]/2 -53),  
                      24,                   -(board_xyz[1]/2),
                      (board_xyz[0]/2 -19), -(board_xyz[1]/2), 1, 20],
                    [ 24,                    (board_xyz[1]/2 -5), 
                      (board_xyz[0]/2 -19),  (board_xyz[1]/2 -5),  
                      24,                   -(board_xyz[1]/2 -21),
                      (board_xyz[0]/2 -19), -(board_xyz[1]/2 -21), 1, 20],

                    [ -5,                    (board_xyz[1]/2 -53), 
                      (board_xyz[0]/2 -28),  (board_xyz[1]/2 -53),  
                      -5,                   -(board_xyz[1]/2),
                      (board_xyz[0]/2 -28), -(board_xyz[1]/2), 1, 20],
                    [ -15,                   (board_xyz[1]/2 -5), 
                      (board_xyz[0]/2 -28),  (board_xyz[1]/2 -5),  
                      -15,                  -(board_xyz[1]/2 -21),
                      (board_xyz[0]/2 -28), -(board_xyz[1]/2 -21), 1, 20],

                    [ 35,                    (board_xyz[1]/2 -17), 
                      (board_xyz[0]/2 +8),   (board_xyz[1]/2 -17),  
                      35,                   -(board_xyz[1]/2 -15),
                      (board_xyz[0]/2 +8),  -(board_xyz[1]/2- 15), 1, 20],

                     
                    [-(board_xyz[0]/2 -6),   (board_xyz[1]/2 -0), 
                     -(board_xyz[0]/2 -15),  (board_xyz[1]/2 -0), 
                     -(board_xyz[0]/2 -6),   (board_xyz[1]/2 -5),
                     -(board_xyz[0]/2 -15),  (board_xyz[1]/2 -5), 1, 20]                     
                     ];              

adapt2head_rot   = [0, 0, 90]; 
adapt2head_offs  = [0, 8, 0]; 


// Adapter
adapter_d        = 46;
adapter_wall_d   = 1.5;
adapter_dz       = 21; //20

adapter_gap1_dy  = 7.5;
adapter_gap1_dz  = 5;
adapter_gap1_dx  = 8;

adapt_rim_r      = 6.5;
neck_scale_xy    = [1.1, 2.3]; //[1.2, 1.7];
neck_offs        = [0, 8, 0];  //[0, 4, 0];

// angle, offset from outer circumfence, dz(outer hole), dz(outer wall), dip, hole diameter, 
// outer hole diameter
adapt_holes_ar   =[[ -30, -2.5,  9,  1.5, 1, 2.0, 4.5, 0], 
                   [  50, -3.0,  9,  4.0, 1, 2.0, 4.5, 0], 
                   [ 180, -3.5,  9,  4.0, 1, 2.0, 4.5, 0],
                   
                   [ 230,  7.0, 12, -2.0, 0, 3.0, 6.5, 0],
                   [ 170, 33.0, 12, -2.0, 0, 3.0, 6.5, 0],
                   [  17,  5.0, 12, -2.0, 0, 3.0, 6.5, 1],
                   
                   [  -5,  5.0, 12, -2.0, 0,   0, 6.5, 2]
                   ];
adapt_post_d     = 6;

adapt_collar_dz  = 4; //4
                    
// ----------------------------------------------------------------------------------
// External parts
// ----------------------------------------------------------------------------------
module board0() 
{   
    rotate(board_rot) translate(board_offs) 
    cube(board_xyz);   
}

module board(show=1)
{
    if(show == 1) {
        %color("OliveDrab", 0.7)
        difference() {
            translate([0, 0, post_dz +board_xyz[2]])
            board0();
            rotate([0, 0, board_z_angle])
            for(h = board_holes_xyd) {
                f_hole([h[0], h[1], 0], h[2], 40, board_offs);
            }
        }
    }
}

module battery0(axy=0)
{       
    rotate(battery_rot) translate([0-axy, 0-axy, base_dz]) translate(battery_offst) 
    cube([battery_xyz[0] +2*axy, battery_xyz[1] +2*axy, battery_xyz[2]]);
}

module battery(show=1)
{
    if(show == 1) {
        %color("yellow", 0.3)
        battery0();
    }
}


module servo0() 
{
    rotate(servo_rot) translate([0, 0, base_dz]) translate(servo_offs) 
    group() {
        cube(servo_xyz);
        translate(servo_offs2) 
        cube(servo_xyz2);
    }    
}

module servo(show=1) 
{
    if(show == 1) {
        %color("blue", 0.7) 
        servo0();
    }
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
module IRSensor_holes(dx) 
{
    translate([15,dx/2,-15])
    group() {
        cylinder($fn=100, h=20, r=1.2);
        translate([0,0,9])
        sphere(6, $fn=100);
    }
}

module IRSensor(hole=0) 
{
    dx1 = 8.5 +0.5;  // 8.5
    dx2 = 10. +0.53;  //10.0
    dy  = 6.3;
    difference() {
        group() {
            translate([0, (dx1-dx2)/2, 1])
            cube([13.6, dx2, dy -1.0]);   
            if(hole == 0) 
                cube([23.8, dx1, 1.0]);   
            else     
                cube([23.8, dx1, dy]);   
        }
        if(hole == 0) 
            IRSensor_holes(dx1);
        else {
            translate([13, (dx1-dx2)/2, 0])
            cube([4,dx2, 1.5]);
        }
    }
    if(hole == 1) 
        IRSensor_holes(dx1);
}

module boardIR0(hole) 
{   
    angx = 0; //-25;
    angz = 30; 
    offx = 2;
    offy = 8;
    
    prm  = [[offx, -offy, angx,  angz],
            [0,        0, angx,     0],
            [offx,  offy, angx, -angz]];

    for(p=prm) {
        translate([p[0], p[1], 0]) rotate([0, p[2], p[3]])
        group() {
            rotate([0,-90,0]) translate([0,-8.5/2,5]) 
            IRSensor(hole);
        }
    }
}

module boardIR(show=1, hole=0)
{
    if(show == 1) {
        translate([-54,-0,-2])
        color("OliveDrab", 0.2)
        boardIR0(hole);
    }
}


// ----------------------------------------------------------------------------------
// Functions
// ----------------------------------------------------------------------------------
module f_hole(pos, d, dz, offs=[0,0,0])
{
    translate(offs) {
        rotate(0, [1,0,0]) 
        translate(pos) translate([0, 0, -dz/2])
        cylinder($fn=100, h=dz, r=d/2);
    }
}

module f_post(pos, d, dz, offs=[0,0,0])
{
    translate(offs) {    
        rotate(0, [1,0,0]) translate(pos)
        cylinder($fn=100, h=dz+base_dz, r=d/2);
    }
}

module f_hull_hole(data)
{
    hull() {
        f_hole([data[0], data[1], 0], data[8], data[9]);
        f_hole([data[2], data[3], 0], data[8], data[9]);
        f_hole([data[4], data[5], 0], data[8], data[9]);
        f_hole([data[6], data[7], 0], data[8], data[9]);
    }
}

// ----------------------------------------------------------------------------------
// HEAD
// ----------------------------------------------------------------------------------
module head() 
{
    difference() {
        group() {
            // baseplate
            color("darkorange", 0.5)
            hull() {
                board0();
                base();
            }
            // edge around board
            color("darkorange", 0.5)
            difference() {
                translate([0,0,1.5])
                board0();

                translate([0,0,0.5])
                scale([0.95, 0.95, 2])
                board0();
            }
            // posts for board
            if(doPosts > 0) {
                color("darkorange", 0.5)
                rotate([0, 0, board_z_angle])
                for(h = board_holes_xyd) {
                    f_post([h[0], h[1], 0], h[2] +post_wall_d*2, post_dz, board_offs);
                }
            }
            
            // battery hold
            color("darkorange", 0.8)
            scale([1, 1, 0.7])
            battery0(axy=1);
            
            // servo mount
            color("darkorange", 0.8)
            translate([-49, 8, 0])
            cube([29, 9, 8]);
        }
        //rotate([0, 0, board_z_angle])
        group() {
            // holes in posts
            rotate([0, 0, board_z_angle])
            for(h = board_holes_xyd) {
                f_hole([h[0], h[1], 0], h[2], 30, board_offs);
            }
            if(doPosts == 0) {
                rotate([0, 0, board_z_angle])
                for(h = board_holes_xyd) {
                    translate([0, 0, 6.5])
                    f_hole([h[0], h[1], 0], h[2]*4, 10, board_offs);
                }
            } 
            
            // gaps in base
            for(g = base_gaps_hulls) {
                f_hull_hole(g);
            }
            // battery
            battery0();
            
            // servo
            servo0();
            
            // Cut around outline
            color("darkorange", 1)
            difference() {
                scale([2, 2, 1])
                scale(base_scale)
                translate([0, 0, -10])
                cylinder($fn=100, h=20, r=base_r);

                scale(base_scale)
                translate([0, 0, -15])
                cylinder($fn=100, h=30, r=base_r);
            }
            
            // Cut off front
            translate([-79, -30, -10])
            cube([30, 60, 20]);
            translate([-68, -30, -10])
            cube([30, 37, 20]);
            translate([-68, 15, -10])
            cube([30, 37, 20]);

            // Cut off back
            translate([50, -30, -10])
            cube([30, 60, 20]);
            
            // Holes
            rotate(-1 *adapt2head_rot) 
            translate(-1 *adapt2head_offs) 
            group() {
                for(h = adapt_holes_ar) {
                    if(h[2] > 10) {
                        x = (adapter_d/2 -adapter_wall_d +h[1]) *sin(-h[0]+180);
                        y = (adapter_d/2 -adapter_wall_d +h[1]) *cos(-h[0]+180);
                        f_hole([x, y, 15], h[5], 80);
                        if(h[2] > 0)  { 
                            if(h[7] > 0) {
                                f_hole([x, y, h[2]], h[6]*2, 21);
                            }
                        }
                    }
                }
            }
            // holes in servo mount
            translate([-23, 15, 4+base_dz])
            rotate([90, 90, 0])
            cylinder($fn=100, h=10, r=1);
            translate([-23 -24, 15, 4+base_dz])
            rotate([90, 90, 0])
            cylinder($fn=100, h=10, r=1);
        }
    }
    // contraptions for battery
  /*color("darkorange", 1)
    group() {
        difference() {
            translate([2, 16, 0])
            cube([15, 2, 3]);
            translate([3.5, 15, -1.5])
            cube([12, 4, 2.5]);
        }
        translate([0, 0, 10])
        difference() {
            translate([2, -16, 0])
            cube([15, 2, 3]);
            translate([3.5, -17, -1.5])
            cube([12, 4, 2.5]);
        }
    }*/

}

// ----------------------------------------------------------------------------------
// SENSOR ARM
// ----------------------------------------------------------------------------------
module sensor_arm() 
{
    dz   = 1;
    dx   = 37;
    r    = 4.0;
    rh   = 1.5;
    llen = 15;
    lhei = 8;
    loff = 0.5;
    lwid = 3 +loff*2; //3
    lgro = 3.5; //6
    offs = -4.5;
    color("gray", 0.8)
    
    translate([-52, 0, r+base_dz]) {
        rotate([0,90,0])
        difference() {
            group() {
                hull() {
                    translate([0, -dx/2, 0])
                    cylinder($fn=100, h=dz, r=r);
                    translate([0, +dx/2, 0])
                    cylinder($fn=100, h=dz, r=r);
                }
                translate([0, offs, 0]) {
                    translate([-lhei/2, -lwid/2 +loff, 0])
                    cube([lhei, lwid, llen -lhei/2 +1]);
                    rotate([90, 90, 0])
                    translate([-lhei*1.2, -lwid/2, 0])
                    cube([lhei*1.2, lwid, lhei*1.2]);
                    
                    rotate([90, 0, 0])
                    translate([0, llen -3, -lwid/2 -loff])
                    cylinder($fn=100, h=lwid, r=lhei/2);

                }
             }
            group() {
                translate([0, -dx/2, -2])
                cylinder($fn=100, h=4, r=rh);
                translate([0, +dx/2, -2])
                cylinder($fn=100, h=4, r=rh);

                translate([0, offs, 0]) {
                    translate([-lgro/2 , -lwid/2 +1.5, dz])
                    cube([lgro, lwid, llen]);
                
                    rotate([90, 0, 0])
                    translate([0, llen -3, -4])
                    cylinder($fn=100, h=8, r=1.2);
                
                    rotate([90, 0, 0])
                    translate([0, llen -3, -4])
                    cylinder($fn=100, h=4.5, r=3);

                    rotate([0, 90, 0])
                    translate([-10, -10, -4])  
                    cylinder($fn=100, h=8, r=8.5);
                }
            }
        }
    }
}
    
// ----------------------------------------------------------------------------------
module sensor_arm_frontPlate_holes(dx, rh) 
{
    translate([0, -dx/2, -2])
    cylinder($fn=100, h=5, r=rh);
    translate([0, +dx/2, -2])
    cylinder($fn=100, h=5, r=rh);
    
    translate([0, -dx/2, -5])
    cylinder($fn=100, h=5, r=rh*1.8);
    translate([0, +dx/2, -5])
    cylinder($fn=100, h=5, r=rh*1.8);   
}


module sensor_arm_frontPlate(dx, dz, r, rh) 
{
    difference() {
        hull() {
            translate([0, -dx/2, 0])
            cylinder($fn=100, h=dz, r=r);
            translate([0, +dx/2, 0])
            cylinder($fn=100, h=dz, r=r);
        }
        sensor_arm_frontPlate_holes(dx, rh);
    }
}

// ----------------------------------------------------------------------------------
module sensor_arm2() 
{
    dz   = 1;
    dx   = 37;
    dy   = 8;
    r    = 4.0;
    rh   = 1.5;
    llen = 15;
    lhei = 8;
    loff = 0.5;
    lwid = 3 +loff*2; //3
    lgro = 3.5; //6
    offs = -4.5;
    lr   = [-1, 1];
    color("Firebrick", 0.8)
    
    translate([-52 -dz, 0, r+base_dz]) {
        rotate([180,270,0])
        difference() {
            group() {
                sensor_arm_frontPlate(dx, dz, r, rh);

                // for photodiode
                for(i = lr) {
                    hull() {
                        translate([0, i*dx/2, 0])
                        cylinder($fn=100, h=dz, r=r);
                        translate([dy, i*dx/2, 0])
                        cylinder($fn=100, h=dz, r=r);
                    }
                    translate([dy, i*dx/2, -15])
                    cylinder($fn=100, h=15, r=4);
                }
             }
             group() {
                 sensor_arm_frontPlate_holes(dx, rh);
                 
                // for photodiode
                for(i = lr) {
                    translate([dy, i*dx/2, -17])
                    cylinder($fn=100, h=17, r=3);
                    translate([dy, i*dx/2-1.5, -2])
                    cylinder($fn=100, h=4, r=rh/2);
                    translate([dy, i*dx/2+1.5, -2])
                    cylinder($fn=100, h=4, r=rh/2);

                    translate([dy-7, i*dx/2 -4 +i*5, -19])
                    cube([8,8,15]);
                    
                }
            }
        }
    }
}


// ----------------------------------------------------------------------------------
module sensor_arm3() 
{
    dz   = 1;
    dx   = 37;
    dy   = 8;
    r    = 4.0;
    rh   = 1.5;
    rdsk = 22;
    rcut = 22; // 15
    color("Tomato", 0.5)

    difference() {
        translate([-52 -dz -1, 0, r+base_dz]) {
            rotate([180,270,0])
            difference() {
                group() {
                    sensor_arm_frontPlate(dx, dz, r, rh);
                
                    translate([-4, 0, 10])
                    rotate([0,90,0])
                    cylinder($fn=100, h=15, r=rdsk);
                }
                group() {
                    sensor_arm_frontPlate_holes(dx, rh);
                    
                    translate([-10, -25, 36])
                    rotate([0,90,0])
                    cube([35,50,25]);
                    
                    translate([-7, 0, 17])
                    rotate([0,90,0])
                    cylinder($fn=100, h=20, r=rcut);
                    
                }
            }
        }
        translate([-55,-0,-2])
        boardIR0(hole=1);    
    }
    color("Tomato", 0.8)
    translate([-52 -dz -1, 0, r+base_dz]) 
    rotate([180,270,0])    
    sensor_arm_frontPlate(dx, dz, r, rh);
}

// ----------------------------------------------------------------------------------
module sensor_arm_amg88xx() 
{
    dz   = 1;
    dx   = 37;
    r    = 4.0;
    rh   = 1.5;
    
    difference() {
        
        group() {
            *color("OliveDrab", 0.7)
            rotate([0,90,0])
            translate([-45,-12.7,-54])
            group() {
                translate([12.7-1.27, 12.7-1.27, -4])
                cube([2.54, 2.54, 4]);
                cube([25.4, 25.4, 1]);
            }
            color("Orange", 0.8)
            difference() {
                translate([-52 -dz, 0, r+base_dz]) {
                    rotate([180,270,0])
                    difference() {
                        group() {
                            rotate([0,25,0])
                            translate([0,0,1.8])
                            sensor_arm_frontPlate(dx, dz, r, rh);
                            translate([0+4, -12.7,0])
                            cube([39.4 -4, 25.4, 1.2]);
                            // ...
                        }
                        group() {
                            rotate([0,25,0])
                            translate([0,0,2])
                            sensor_arm_frontPlate_holes(dx, rh);
                            translate([30, -8,-1])
                            cube([10, 16, 3]);
                            translate([10, -8,-1])
                            cube([10, 16, 3]);
                            
                        }
                    }
                }
            }
        }
        rotate([0,90,0])
        translate([-45,-12.7,-54])
        group() {
            translate([2.54, 2.54, -2.5])
            cylinder($fn=100, h=15, r=1.4);
            translate([0.9*25.4, 2.54, -2.5])
            cylinder($fn=100, h=15, r=1.4);
            translate([0.9*25.4, 0.9*25.4, -2.5])
            cylinder($fn=100, h=15, r=1.4);
            translate([2.54, 0.9*25.4, -2.5])
            cylinder($fn=100, h=15, r=1.4);
        }
    }
}

// ----------------------------------------------------------------------------------
module ring() 
{
    color("brown", 0.6)
    difference() {
        group() {
            translate([0, 0, 0])
            cylinder($fn=100, h=2, r=2.5);
            translate([0, 0, 2])
            cylinder($fn=100, h=1, r=4);
        }
        translate([0, 0, -5])
        cylinder($fn=100, h=10, r=3/2);
    }
}


// ----------------------------------------------------------------------------------
// NECK/ADAPTER
// ----------------------------------------------------------------------------------
module base()
{
    color("goldenrod", 0.6)
    scale(base_scale)
    cylinder($fn=100, h=base_dz, r=base_r);
}    

module adapter_base()
{
    difference() {
        group() {
            color("darkorange", 0.6)
            cylinder($fn=100, h=adapter_dz, r=adapter_d/2);
            
            color("darkorange", 0.6)
            translate([0, 0, adapter_dz])
            linear_extrude(height=adapt_collar_dz, center=true, convexity=10, 
                           scale=neck_scale_xy, $fn=100)
            translate(neck_offs)
            circle($fn=100, r=adapter_d/2);
        }
        group() {
            translate([0,0,-1])
            cylinder($fn=100, h=adapter_dz, r=adapter_d/2 -adapter_wall_d);

            translate([0,0,-1])
            cylinder($fn=100, h=adapter_dz+20, r=adapter_d/2 -adapter_wall_d -adapt_rim_r);

            translate([-5, -adapter_gap1_dy/2 -adapter_d/2, -1])
            cube([adapter_gap1_dx, adapter_gap1_dy, adapter_gap1_dz +1]);

            rotate([0,0,-90])
            translate([-5, -adapter_gap1_dy/2 -adapter_d/2 +6.5, adapter_dz -2.5])
            cube([10, 6, 5]);
        }
    }
    color("orange", 0.3) 
    group() {
        for(h = adapt_holes_ar) {
            x = (adapter_d/2 -adapter_wall_d +h[1]) *sin(-h[0]+180);
            y = (adapter_d/2 -adapter_wall_d +h[1]) *cos(-h[0]+180);
            f_post([x, y, 15.5- h[3] +3], adapt_post_d, h[3]);
        }
    }
}

module adapter() 
{
    difference() {
        adapter_base();      
        group() {
            for(h = adapt_holes_ar) {
                if(h[7] < 2) {
                    x = (adapter_d/2 -adapter_wall_d +h[1]) *sin(-h[0]+180);
                    y = (adapter_d/2 -adapter_wall_d +h[1]) *cos(-h[0]+180);
                    f_hole([x, y, 15], h[5], 20);
                    if(h[2] > 0) { 
                        f_hole([x, y, h[2]], h[6], 20);
                    }   
                    if(h[4] > 0) {     
                        translate([x, y, adapter_dz +5])
                        //scale([1,1,0.6])
                        //sphere(8, $fn=100); 
                        scale([1,1,0.7])
                        sphere(6, $fn=100); 
                    }
                }
            }
            // Cut off back
            rotate([0, 0, 90])
            translate([58, -30, 10])
            cube([30, 60, 20]);

            // Cut off front
            rotate([0, 0, 90])
            translate([-60, -30, 10])
            cube([30, 60, 20]);
            
            // Motor connector cut-out
            rotate([0, 0, 90])
            translate([8, 0, 20])
            f_hull_hole(base_gaps_hulls[0]);

            rotate([0, 90, 125 +board_z_angle +45])
            translate([-13,0,15])
            //cylinder($fn=100, h=10, r=6.5); 
            cylinder($fn=100, h=10, r=6); 
        }
    }
}


// ----------------------------------------------------------------------------------
translate(adapt2head_offs) 
rotate(adapt2head_rot) 
group() {
    board(showBoard);
    battery(showBattery);
    servo(showServo);
    boardIR(showboardIR);
    head();
    sensor_arm();
    *sensor_arm2();
    sensor_arm3();
    translate([-9,0,-22])
    rotate([0,25,0])
    sensor_arm_amg88xx();
}

*sensor_arm();
*sensor_arm2();
*sensor_arm3();
*sensor_arm_amg88xx();

translate([0, 0,-23]) 
adapter();

*ring();
    
// ----------------------------------------------------------------------------------