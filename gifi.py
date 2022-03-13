import grid_draw as gd
import numpy as np
import sys
import imageio
import argparse
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser(description="This is a tool for visualizing plans generated by the fast downward tool.\n\nThis tool is specifically designed to accompany work relating to RHUL CS5980 Final Project. It is basically useless otherwise")

parser.add_argument("-p", "--prob", type=str, 
    help="The problem(.pddl) file for the accomanying plan")
parser.add_argument("-s", "--sas_plan", type=str, 
    help="The plan(sas_plan by default) file for the accomanying problem")

parser.add_argument("-l", "--light", type=str, 
    help="The path to the image used for lights, by default ./light.png")
parser.add_argument("-b", "--black", type=str, 
    help="The path to the image used for black squares, by default ./black.png")

parser.add_argument("-o", "--output", type=str,
    help="The output destination for the generated gif")

args = parser.parse_args()

if args.prob is not None:
    with open(args.prob) as prob_src:
        prob_str = prob_src.read()
        gs = gd.get_gs_from_src(prob_str)
        surrounds, blacks = gd.get_blacks_from_src(prob_str)
else:
    print("(-p, --prob missing) No problem file given, use -h for help")
    exit(1)

if args.sas_plan is not None:
    with open(args.sas_plan) as plan_src:
        plan_str = plan_src.read()
        bulbs = gd.get_bulbs_from_plan(plan_str)
else:
    print("(-s, --sas_plan missing) No plan file given, use -h for help")
    exit(1)

if args.light is not None:
    BULB_IMG = args.light
else:
    BULB_IMG = "./bulb.png"
       
if args.black is not None:
    BLACK_IMG = args.black
else:
    BLACK_IMG = "./black.png"

UNIT = 100
LIGHT = "rgba(252, 186, 3, 55)"

def make_gif():

    base = gd.draw_grid([], blacks, surrounds, gs, UNIT, black_img=BLACK_IMG)
    img_seq = [base.copy()] * 5
    bulb_img = Image.open(BULB_IMG).resize((UNIT,UNIT))

    lit = np.zeros((gs, gs), dtype=int)

    for bulb in bulbs:
        x = bulb[0]*UNIT
        y = bulb[1]*UNIT
        base.paste(bulb_img, [x,y,x+UNIT,y+UNIT], mask=bulb_img)
        light_up = propogate(lit.copy(), bulb, blacks)

        light_imgs = []
        for l in light_up:
            lit += l
            c_lm = get_light_map(lit, LIGHT, UNIT)
            c_img = base.copy()
            c_img.alpha_composite(c_lm)
            light_imgs.append(c_img)

        img_seq += light_imgs

    lit_up = np.sum([[min(1, n) for n in k] for k in lit]) + len(blacks) < lit.shape[0]
    overlaps = len(set(bulbs).intersection(set(blacks))) > 0
    if not lit_up or overlaps:
        print("Looks like the plan you gave doesn't solve the accompanied problem. \
               \nMake sure a valid plan was found. The resulting gif might look very weird...")
    
    return img_seq

def propogate(lit, bulb, blacks):
    lim = lit.shape[0]

    bx = bulb[0]
    by = bulb[1] 
    
    lit[bx, by] = 1
    
    l = r = u = d = True
    dist = 0

    light_states = []

    while l or r or u or d:
        cl = bx-dist
        cr = bx+dist
        cu = by-dist
        cd = by+dist
    
        l = (cl, by) not in blacks and cl >= 0 and l
        r = (cr, by) not in blacks and cr < lim and r
        u = (bx, cu) not in blacks and cu >= 0 and u
        d = (bx, cd) not in blacks and cd < lim and d
        
        if l:
            lit[cl, by] = 1
        if r:
            lit[cr, by] = 1
        if u:
            lit[bx, cu] = 1
        if d:
            lit[bx, cd] = 1
           
        light_states.append(lit.copy())
        dist += 1

    return light_states


def get_light_map(lit, light_val, UNIT=100):
    dim = (lit.shape[0] * UNIT, lit.shape[1] * UNIT)
    lm = Image.new("RGBA", dim)
    lmd = ImageDraw.Draw(lm)

    for i in range(lit.shape[0]):
        x = i * UNIT
        for j in range(lit.shape[1]):
            y = j * UNIT
            if lit[i, j] > 0:
                lmd.rectangle([x, y, x+UNIT,y+UNIT], fill=light_val)

    return lm

if __name__ == "__main__":
    imgs = make_gif()    
    imgs[0].save("./plan.gif", save_all=True, append_images=imgs[1:], duration=100, loop=1)


