import os
import sys
from PIL import Image, ImageFont, ImageDraw
from shutil import copyfile

# =======
results_folder = "3_robobrain/2021-12-16_16-06-00-robobrain-M1"
#results_folder = "1_nrpexperiment_scale20-threads72-nodes16-nvp1152-withoutTF/2021-12-10_16-15-40-hpcbench_notf"
run_folder = 4
sacct = True
# =======

base_path = os.getcwd()
figure_path = os.path.join(base_path, "Results", results_folder, "paper_figures")
if not os.path.exists(figure_path):
    os.mkdir(figure_path)


horizontal_distance = 5
vertical_distance = 5

def create_image(image_files, max_per_row=2):
    """
    Creates a new figure by merging several jpg images.
    :param image_files: list with image file names.
    :param max_per_row: maximal number of images per row.
    """

    images = [Image.open(os.path.join(base_path, "Results", results_folder, \
                                    "diagrams", x)) for x in image_files]
    widths, heights = zip(*(i.size for i in images))

    print("len image files ", len(image_files))
    total_width = max_per_row * max(widths) + (max_per_row - 1)* horizontal_distance
    total_height = (len(image_files)/max_per_row) * max(heights) \
        + (len(image_files) / max_per_row-1)* vertical_distance
    if len(image_files) % max_per_row != 0:
        total_height += max(heights)

    print("total width {} total height {}".format(total_width, total_height))
    new_im = Image.new('RGB', (total_width, total_height), color = (255,255,255))


    x_offset = 0
    y_offset = 0
    im_last_row = max_per_row
    nr_last_row = 0
    for i in range(len(image_files)):
        title_text = "The Beauty of Nature"
        print("y_offset", y_offset)
        print('i is ', i)
        # create tag
        img = Image.new('RGB', (50, 50), (255,255,255))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("OpenSans-Regular.ttf", 30)
        draw.text((20, 2),str(chr(97+i))+")",(0,0,0),font=font)

        new_im.paste(images[i], (x_offset, y_offset))
        new_im.paste(img, (x_offset, y_offset))
        x_offset += images[i].size[0] + horizontal_distance
        if (i+1) % max_per_row == 0:
            x_offset = 0
            print('next row', images[i].size[0], images[i].size[1])
            y_offset += images[i].size[1] + vertical_distance
            if len(image_files)- (i+1) < max_per_row:
                im_last_row = len(image_files)- (i+1)

        print("im_last_ros ", im_last_row)
        if im_last_row < max_per_row and im_last_row != 0:
            print('nr_last_row ', nr_last_row)
            x_offset = (total_width / (im_last_row + 1)-  max(widths)/2) \
                    + nr_last_row *  max(widths)
            nr_last_row += 1

    return new_im


## =============================================================================
## Runtime Realtime
image_files = ["total_runtime-one.jpg",
               "raltime_factors-one.jpg"]

new_im = create_image(image_files, max_per_row=2)

new_im.save(os.path.join(figure_path, results_folder.replace("/", "--") + '--runtime_realtime.jpg'))



## =============================================================================
## NEST times
image_files = ["nest_time_create-one.jpg",
                "nest_time_connect-one.jpg",
                "nest_time_last_simulate-one.jpg"]

new_im = create_image(image_files, max_per_row=2)

new_im.save(os.path.join(figure_path, results_folder.replace("/", "--") + '--nest_times.jpg'))


## =============================================================================
# sacct param
if sacct == True:
    image_files = ["sacct_maxrss-one.jpg",
                   "sacct_consumedenergy-one.jpg"]

    new_im = create_image(image_files, max_per_row=2)

    new_im.save(os.path.join(figure_path, results_folder.replace("/", "--") + '--sacct.jpg'))


## =============================================================================
# cle profiler param
image_files = ["cle_time_profile-brain_step-one.jpg",
               "cle_time_profile-robot_step-one.jpg",
               "cle_time_profile-transfer_function-one.jpg",
               "cle_time_profile-brain_step-one-second.jpg",
               "cle_time_profile-robot_step-one-second.jpg",
               "cle_time_profile-transfer_function-one-second.jpg"]

new_im = create_image([str(run_folder) + "/" + img for img in image_files], max_per_row=3)

new_im.save(os.path.join(figure_path, results_folder.replace("/", "--") + '--cle-profile.jpg'))


## =============================================================================
# brain to robot ratio
copyfile(os.path.join(base_path, "Results", results_folder, "diagrams", \
                      str(run_folder) + "/braintorobot_ratio.jpg"),
          os.path.join(figure_path, figure_path, results_folder.replace("/", "--")
                       + '--braintorobot_ratio.jpg'))
