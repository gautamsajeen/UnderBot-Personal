"""WR141E exterior reconstructed from online reference views.

Envelope and wheel diameters have published/supplier evidence. Surface stations,
rear tyre width, axle locations and controls are image-derived, not factory CAD.
Coordinates: metres, x forward, y left, z up. No cutting blade is modelled.
"""
import math
import numpy as np


def rounded_outline(points, count=8):
    p=np.asarray(points,float); result=[]
    for i,b in enumerate(p):
        a=b+(p[i-1]-b)*.24;c=b+(p[(i+1)%len(p)]-b)*.24
        for t in np.linspace(0,1,count,endpoint=False):
            result.append((1-t)**2*a+2*t*(1-t)*b+t*t*c)
    q=np.array(result)
    # Retain the specified station envelope after rounding the corners.
    q=(q-q.min(0))/(q.max(0)-q.min(0))*(p.max(0)-p.min(0))+p.min(0)
    if np.sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1))<0:q=q[::-1]
    return q


def loft(api, link, name, outline, layers, color, mass=0):
    poly=rounded_outline(outline);n=len(poly);center=(poly.max(0)+poly.min(0))/2
    vertices=[]
    for scale,z in layers:
        for x,y in (poly-center)*scale+center:
            vertices.append([x,y,z(x,y) if callable(z) else z])
    # Side quads are triangulated here to make the exact public geometry explicit.
    faces=[]
    for k in range(len(layers)-1):
        for i in range(n):
            j=(i+1)%n;a=k*n+i;b=k*n+j;c=(k+1)*n+j;d=(k+1)*n+i
            faces += [[a,b,c],[a,c,d]]
    for a,b,c in api['earclip'](poly):
        faces += [[c,b,a],[a+(len(layers)-1)*n,b+(len(layers)-1)*n,c+(len(layers)-1)*n]]
    v=np.array(vertices);origin=(v.max(0)+v.min(0))/2
    part=api['part'](link,name,'loft',np.ptp(v,axis=0),origin,color=color,mass=mass)
    part.update(vertices=(v-origin).tolist(),faces=faces,dimension_basis='online image-derived surface stations',
                smoothing=True,assembly='wr141e_base')
    return part


def build_body(api,P):
    box,cyl,collision=api['box'],api['cyl'],api['collision']
    BLACK,DARK,ORANGE,RED,METAL=map(api.get,('BLACK','DARK','ORANGE','RED','METAL'))
    base='base_link'
    # Rear chassis is narrow between the wheels, broadens into the rounded nose.
    deck=[(-.279,-.140),(-.249,-.145),(-.105,-.145),(-.072,-.180),
          (.000,-.193),(.157,-.193),(.223,-.167),(.264,-.109),(.274,0),
          (.264,.109),(.223,.167),(.157,.193),(.000,.193),(-.072,.180),(-.105,.145),(-.249,.145),(-.279,.140)]
    def chassis_top(x,y):return .153-.032*max(0,(x-.080)/.194)
    loft(api,base,'wr141e_lower_chassis',deck,[(.94,.049),(1.,.065),(1.,.113),(.96,chassis_top)],BLACK,P['retained_chassis_mass']-.55)
    nose=[(-.084,-.178),(-.055,-.198),(.125,-.202),(.203,-.184),(.259,-.128),(.279,-.047),
          (.279,.047),(.259,.128),(.203,.184),(.125,.202),(-.055,.198),(-.084,.178)]
    def lower(x,y):
        # The cut-to-edge/front guard is on the robot's RIGHT, not a full-width grille.
        return .057 + .038*max(0,min(1,(-y-.005)/.060))*max(0,min(1,(x+.040)/.080))
    def shoulder(x,y):return .161-.032*max(0,(x-.125)/.154)
    def crown(x,y):return .175-.026*max(0,(x+.010)/.289)
    loft(api,base,'wr141e_orange_hood',nose,[(.995,lower),(1.,lambda x,y:lower(x,y)+.012),
        (1.,shoulder),(.93,lambda x,y:shoulder(x,y)+.018),(.79,crown)],ORANGE,.55)
    upper=[(-.279,-.137),(-.240,-.145),(-.090,-.145),(-.040,-.151),(.105,-.150),
           (.157,-.121),(.177,-.066),(.168,0),(.177,.066),(.145,.128),(.105,.147),
           (-.080,.147),(-.240,.145),(-.279,.137)]
    # A planar cap prevents a long triangulation chord from dipping through
    # the orange shoulder behind the control pod.
    def top(x,y):return .183-.040*(x+.035)
    loft(api,base,'wr141e_black_upper_deck',upper,[(1.,.145),(1.,lambda x,y:top(x,y)-.005),(.97,top)],DARK)
    hatch=[(-.271,-.124),(-.252,-.136),(-.127,-.136),(-.099,-.104),(-.094,0),
           (-.099,.104),(-.127,.136),(-.252,.136),(-.271,.124)]
    loft(api,base,'wr141e_rear_battery_hatch',hatch,[(1.,.177),(.98,.187),(.86,.195),(.73,.198)],DARK)
    box(base,'battery_hatch_release',[.025,.014,.003],(-.245,0,.1995),c=BLACK)
    # Dark right-side cut-to-edge insert, curved front comb and left moulding seam.
    for y in (-.196,.196):
        box(base,'side_lower_seam_'+str(y),[.150,.003,.003],(.052,y,.104),c=DARK)
    box(base,'cut_to_edge_right_insert',[.195,.005,.049],(.070,-.195,.073),c=DARK)
    for i,y in enumerate(np.linspace(-.162,-.012,10)):
        x=.279-.22*y*y/.040
        # Swept fingers follow the rounded right half. Keep them above the wheel sweep.
        box(base,'right_front_guard_tooth_'+str(i),[.017,.005,.043],(x-.016,y,.074),r=(0,-.20,0),c=DARK)
    # Distinct height dial and STOP/keypad pod, correctly handed in ROS axes.
    cyl(base,'height_adjustment_surround',.060,.010,(.063,-.089,.176),c=BLACK)
    cyl(base,'height_adjustment_dial',.049,.011,(.063,-.089,.1865),c=ORANGE)
    box(base,'height_dial_grip',[.016,.090,.015],(.063,-.089,.195),c=ORANGE)
    for i in range(7):
        a=math.radians(-80+i*27)
        box(base,'height_dial_tick_'+str(i),[.003,.004,.001],(.063+.054*math.cos(a),-.089+.054*math.sin(a),.182),c=METAL)
    pod=[(-.050,.000),(-.036,-.010),(.090,-.010),(.103,.004),(.103,.081),(.090,.095),(-.036,.095),(-.050,.082)]
    loft(api,base,'control_pod',pod,[(1.,.174),(1.,.179),(.91,.184)],BLACK)
    box(base,'stop_button',[.039,.072,.016],(-.018,.043,.192),c=RED)
    box(base,'display',[.056,.067,.002],(.054,.043,.185),c=BLACK)
    # Raised keypad row and four simple seven-segment display digits.
    for y in (.017,.035,.053,.071):
        box(base,'display_key_'+str(y),[.010,.011,.001],(.026,y,.1865),c=METAL)
    led=api['GREEN']
    for digit,y in enumerate((.021,.036,.051,.066)):
        for k,x in enumerate((.050,.059,.068)):
            box(base,f'display_led_{digit}_{k}',[.0012,.008,.0005],(x,y,.1863),c=led)
        for k,(x,dy) in enumerate(((.0545,-.004),(.0545,.004),(.0635,-.004),(.0635,.004))):
            box(base,f'display_led_side_{digit}_{k}',[.006,.0012,.0005],(x,y+dy,.1863),c=led)
    box(base,'rain_sensor_insert',[.031,.017,.005],(-.025,-.125,.189),c=BLACK)
    for x in (-.032,-.018):cyl(base,'rain_pin_'+str(x),.002,.001,(x,-.125,.192),c=METAL)
    # Red side charging housing: two rounded contacts, never at the rear.
    box(base,'charge_mount',[.131,.027,.043],(.061,-.170,.161),c=BLACK)
    box(base,'side_charging_contact_bar',[.122,.015,.031],(.061,-.1875,.159),c=RED)
    for x in (.025,.097):
        cyl(base,'charging_contact_lobe_'+str(x),.014,.018,(x,-.189,.159),(math.pi/2,0,0),RED)
        box(base,'charging_contact_'+str(x),[.027,.003,.004],(x,-.1995,.156),c=METAL)
    # Deliberately simpler collision proxies stay inside the exterior envelope.
    collision(base,'rear_chassis','box',[.370,.280,.105],(-.090,0,.1175))
    for sign in (-1,1):collision(base,'nose_side_'+str(sign),'box',[.150,.065,.070],(.155,sign*.133,.105))
    collision(base,'nose_upper','box',[.180,.280,.035],(.160,0,.143))
    for p in api['links'][base]['parts']:p.setdefault('assembly','wr141e_base')


def build_wheel(api, wheel, P):
    cyl,box=api['cyl'],api['box'];BLACK,DARK=api['BLACK'],api['DARK'];pi=math.pi
    r,w=P['wheel_radius'],P['wheel_width']
    cyl(wheel,'rubber_tyre',r,w,r=(pi/2,0,0),c=BLACK,m=P['wheel_mass']*.8)
    cyl(wheel,'hub',r*.85,w-.006,r=(pi/2,0,0),c=DARK,m=P['wheel_mass']*.2)
    for side in (-1,1):
        cyl(wheel,f'wheel_recess_{side}',r*.745,.001,(0,side*(w/2-.0024),0),(pi/2,0,0),BLACK)
        for k in range(3):
            angle=2*pi*k/3+pi/2
            box(wheel,f'wheel_spoke_{side}_{k}',[.059,.004,.017],(.054*math.cos(angle),side*(w/2-.002),.054*math.sin(angle)),
                (0,-angle,0),DARK)
        cyl(wheel,f'wheel_hub_cap_{side}',.031,.003,(0,side*(w/2-.0015),0),(pi/2,0,0),DARK)
