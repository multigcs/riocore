# install libs:

sudo apt-get install libspnav-dev spacenavd
git clone https://github.com/mastersign/pyspacenav.git
cd pyspacenav
sudo python3 setup.py install


# manual hal configuration

loadusr -Wn spacenav ./spnav.py

setp spacenav.axis.x.scale -0.2
setp spacenav.axis.y.scale -0.2
setp spacenav.axis.z.scale 0.2
setp spacenav.axis.a.scale 0.02
setp spacenav.axis.b.scale 0.02
setp spacenav.axis.c.scale 0.02

net spacenav_x <= spacenav.axis.x.jog-counts
net spacenav_x => axis.x.jog-counts
setp axis.x.jog-vel-mode 1
setp axis.x.jog-enable 1
setp axis.x.jog-scale 0.01

net spacenav_y <= spacenav.axis.y.jog-counts
net spacenav_y => axis.y.jog-counts
setp axis.y.jog-vel-mode 1
setp axis.y.jog-enable 1
setp axis.y.jog-scale 0.01

net spacenav_z <= spacenav.axis.z.jog-counts
net spacenav_z => axis.z.jog-counts
setp axis.z.jog-vel-mode 1
setp axis.z.jog-enable 1
setp axis.z.jog-scale 0.01

net spacenav_c <= spacenav.axis.c.jog-counts
net spacenav_c => axis.c.jog-counts
setp axis.c.jog-vel-mode 1
setp axis.c.jog-enable 1
setp axis.c.jog-scale 0.01

