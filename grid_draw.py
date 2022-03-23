from PIL import Image, ImageDraw, ImageFont
import numpy as np
import sys
import re

def get_gs_from_src(src):
    pos_nums = []
    for xy in re.findall(r"[XY](\d+) - [xy]pos", src):
        pos_nums.append(int(xy))

    return max(pos_nums) + 1

def get_blacks_from_src(src):
    surrounds = {}
    blacks = []

    for surr in re.findall(r"\(surrounded X(\d+) Y(\d+) N(\d+)\)", src):
        s0 = int(surr[0])
        s1 = int(surr[1])
        surrounds[(s0, s1)] = surr[2]
    
    for black in re.findall(r"\(black X(\d+) Y(\d+)\)", src):
        b0 = int(black[0])
        b1 = int(black[1])
        blacks.append((b0, b1))

    return surrounds, blacks
    
def get_bulbs_from_plan(plan):
    bulbs = []
    for bulb in re.findall(r"\(light-up x(\d+) y(\d+)\)", plan):
        bulbs.append((int(bulb[0]), int(bulb[1])))
    
    return bulbs


def draw_grid(bulbs, blacks, surrounds, gs, UNIT=100, bulb_img="./bulb.png", black_img="./black.png"):
    # build a font
    fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 50)

    # build an image and a draw interface
    size = (UNIT * gs, UNIT * gs)
    base_img = Image.new("RGBA", size, "rgba(0,0,0,0)")
    draw = ImageDraw.Draw(base_img)

    # load in bulb images
    bulb_base_img = Image.open(bulb_img).resize((UNIT, UNIT))
    black_base_img = Image.open(black_img).resize((UNIT, UNIT))

    # default background and "true black"
    BACKGROUND = "white"
    LIGHT = "rgba(252, 186, 3, 55)"
    BLACK = "black"


    for x in range(gs):

        x_pos = x * UNIT

        for y in range(gs):

            y_pos = y * UNIT
            box = [x_pos,y_pos,x_pos+UNIT,y_pos+UNIT]
            draw.rectangle(box, fill=BACKGROUND, outline="black", width=2)

            if (x, y) in surrounds.keys():
                base_img.paste(black_base_img, box, mask=black_base_img)
                draw.text((x_pos + (UNIT / 2) - 15, y_pos + (UNIT / 2) - 25), 
                    str(surrounds[(x,y)]), 
                    anchor="mb", 
                    align="center", 
                    font=fnt, 
                    stroke_width=2)

            elif (x, y) in blacks:
                base_img.paste(black_base_img, [x_pos,y_pos,x_pos+UNIT,y_pos+UNIT], mask=black_base_img)


    prop_imgs = []

    for bulb in bulbs:
        x = bulb[0]*UNIT
        y = bulb[1]*UNIT
        base_img.paste(bulb_base_img, [x,y,x+UNIT,y+UNIT], mask=bulb_base_img)
        
    return base_img


if __name__ == "__main__":

    gs = 5

    if len(sys.argv) > 2:
        with open(sys.argv[1]) as prob_src:
            prob_str = prob_src.read()
            gs = get_gs_from_src(prob_str)
            surrounds, blacks = get_blacks_from_src(prob_str)

        with open(sys.argv[2]) as plan_src:
            plan_str = plan_src.read()
            bulbs = get_bulbs_from_plan(plan_str)

    BULB_IMG = "./bulb.png"
    BLACK_IMG = "./black.png"

    draw_grid(bulbs, blacks, surrounds, gs, BULB_IMG, BLACK_IMG).show()

