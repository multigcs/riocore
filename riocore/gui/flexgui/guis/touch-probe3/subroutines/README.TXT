USE AT YOUR OWN RISK!
Note: due to the nature of tool setter locaions and cnc setups
the p_tool.ngc has been left in for a GUIDE ONLY. Deternine what works
best for your setup. Feel free to modify these routines to your liking. 

To make user variables persistent create an entry in the .var file for each one as indicated.
2000	0.000000
2001	0.000000
. . . .
2110	0.000000

The values entered from the UI will be saved to the .var file loaded upon startup and 
updated as changes are made. The following user number variables are used or reserved
for use with these probe routines.
Some are used in the UI file and some are workspace variables.

#2000	probing SEARCH_FEED
#2001	probing FINE_FEED
#2002	probing SEARCH_DIST
#2003	probing RETRACT_DIST
#2004	probing XY_travel_dist
#2005	probing offset dist to begin corner probing
#2006	probing X start point for corners, bolt pattern center & hole mill
#2007	probing Y start point for corners, bolt pattern center & hole mill
#2008	probing Z max for bar & tool
#2009	probing tool Z Start dist
#2010	probing max hole radius
#2011	probing max bar radius
#2012	probing probe tip radius calc
#2013	probing angle_base_dist
#2014	probing angle first point
#2015	probing Probe tip Diam from UI
#2016	probing var angles, dist, bar, hole
#2017	probing var angles, dist, bar, hole
#2018	probing var angles, dist, bar, hole
#2019	probing var bar & hole
#2020	probing var dist, bar, hole
#2021	probing var dist, bar, hole
#2022	probing var bar
#2023	probing var bar
#2024	probing X Result
#2025	probing Y Result
#2026	probing Z Result
#2027	probing var in p_hole
#2028	probing var in p_hole
#2029	probing var in p_hole
#2030	probing var in p_hole
#2031	probing var in p_hole
#2032	probing angle XY search dist
#2033	probing setter X coord reserved
#2034	probing setter Y coord reserved
#2035	probing setter Z coord reserved
#2036	probing Z-safe for edge probe routines

#2037	hole pattern diameter
#2038	hole pattern hole count
#2039	hole pattern start angle
#2040	hole pattern angle increment
#2041	hole pattern start
#2042	hole pattern Z depth
#2043	hole pattern Radius
#2044 	hole pattern Feedrate
#2045 	hole pattern Clear Return point
#2046	hole pattern spindle rpm

#2047	hole mill tool diameter
#2048	hole mill depth of cut
#2049	hole mill current depth step
#2050	hole mill Z Clear Return point
#2051	hole mill Z depth
#2052	hole mill diameter
#2053	hole mill feedrate
#2054	hole mill spindle rpm
#2055	hole mill X start point 
#2056	hole mill Y start point 
#2057	countersink pattern angle increment additive
#2058	temp counter for restore
#2059	Q word for G83 drill cycle

#2060	tap X Center
#2061	tap Y Center
#2062	tap Z Start
#2063	tap Z Clear
#2064	tap Z Depth
#2065	tap TPI
#2066	tap IPR calculated from TPI
#2067	tap Spindle rpm
#2068	tap Feed ( for linear moves only)

#2069	slot X1 
#2070	slot Y1 
#2071	slot X2 
#2072	slot Y2 
#2073	slot width 
#2074	slot depth 
#2075	slot Z Clear 
#2076	slot tool dia
#2077	slot feed
#2078	slot spindle rpm
#2079	slot tool radius
#2080	slot ramp percent of T diam
#2081	slot calc
#2082	slot calc
#2083	slot calc
#2084	slot calc
#2085	slot calc
#2086	slot calc
#2087	slot calc
#2088	slot calc

#2089 threadmill FORM = #INTERN0_EXTERN1
#2090 threadmill DIR_RH0_LH1 is direction of thread RH THREAD = 0, LH THREAD = 1
#2091 threadmill THREADS is threads per inch
#2092 threadmill MAJOR_DIAMETER is just that
#2093 threadmill MINOR_DIAMETER is just that
#2094 threadmill NO_OF_PASSES is the number of passes to create
#2095 threadmill THREADMILL_D is diameter of the single point cutter
#2096 threadmill FULL_THREADS how many full threads do you want
#2097 threadmill CENTER_X locates the helix X center
#2098 threadmill CENTER_Y locates the helix Y center
#2099 threadmill START_Z locates the start of thread for Z (leadin move added above this)
#2100 threadmill feedrate
#2101 threadmill spindle rpm
#2102 threadmill pitch calc
#2103 threadmill total pitch
#2104 threadmill first helix
#2105 threadmill final helix
#2106 threadmill od start calc
#2107 threadmill pass count work var
#2108 threadmill Threadmill Radius

#2109 probing X- bar first pass edge Result
#2110 probing Y- bar first pass edge Result

#2111	reserved
#2112	reserved
#2113	reserved
#2114	reserved
#2115	reserved
#2116	reserved
#2117	reserved
#2118	reserved
#2119	reserved
#2120	reserved

