#!/usr/bin/env python
#coding=utf-8
import sys
import os
from svgutils.compose import *
from shutil import copyfile

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <datadir1> [<datadir2> ...]")

# =======
results_folder =  sys.argv[1]
run_folder = 4
# =======

print('results folder ', results_folder)

figure_path = os.path.join(results_folder, "paper_figures")
figure_path_png = os.path.join(figure_path, "png")
os.makedirs(figure_path_png)

exp_name = ""
if "fullbrain" in results_folder:
    exp_name = "fullbrain"
elif "hpc" in results_folder:
    exp_name = "hpc"
elif "smallbrain" in results_folder:
    exp_name = "smallbrain"

## =============================================================================
## Runtime Realtime
print('results folder ', results_folder)

Figure("15.2cm", "5.6cm",
       Panel(
           SVG("comparison_figures/white.svg")
       ),
       Panel(
             SVG(os.path.join(results_folder, "diagrams", "total_runtime.svg")),
             Text("(A)", 25, 20, size=18, weight='bold')
            ).move(0, 0).scale(0.013),
        Panel(
              SVG(os.path.join(results_folder, "diagrams", "realtime_factors.svg")),
              Text("(B)", 25, 20, size=18, weight='bold')
             ).move(600, 0).scale(0.013),
        ).save(os.path.join(figure_path, exp_name + "--runtime_realtime.svg"))

os.system("inkscape " + os.path.join(figure_path, exp_name + "--runtime_realtime.svg")
          + " --export-png=" + os.path.join(figure_path_png, exp_name + "--runtime_realtime.png")
          + " --export-dpi=600")


## =============================================================================
## NEST + sacct times

Figure("15.2cm", "11.2cm",
       Panel(
           SVG("comparison_figures/white.svg")
       ),
       Panel(
             SVG(os.path.join(results_folder, "diagrams", "nest_time_build.svg")),
             Text("(A)", -2, 20, size=18, weight='bold')
            ).move(0, 0).scale(0.013),
        Panel(
              SVG(os.path.join(results_folder, "diagrams", "nest_time_last_simulate.svg")),
              Text("(B)", -2, 20, size=18, weight='bold')
             ).move(600, 0).scale(0.013),
       Panel(
             SVG(os.path.join(results_folder, "diagrams", "sacct_maxrss.svg")),
             Text("(C)", -2, 20, size=18, weight='bold')
            ).move(0, 440).scale(0.013),
        Panel(
              SVG(os.path.join(results_folder, "diagrams", "sacct_consumedenergy.svg")),
              Text("(D)", -2, 20, size=18, weight='bold')
             ).move(600, 440).scale(0.013),
        ).save(os.path.join(figure_path, exp_name + "--nest_sacct.svg"))

os.system("inkscape " + os.path.join(figure_path, exp_name + "--nest_sacct.svg")
          + " --export-png=" + os.path.join(figure_path_png, exp_name + "--nest_sacct.png")
          + " --export-dpi=600")

## =============================================================================
# cle profiler param

Figure("15.6cm", "3.9cm",
       Panel(
           SVG("comparison_figures/white.svg")
       ),
       Panel(
             SVG(os.path.join(results_folder, "diagrams", str(run_folder), "cle_time_profile-brain_refresh.svg")),
             Text("(A)", 25, 20, size=18, weight='bold')
            ).move(0, 0).scale(0.009),
        Panel(
              SVG(os.path.join(results_folder, "diagrams", str(run_folder), "cle_time_profile-robot_step.svg")),
              Text("(B)", 25, 20, size=18, weight='bold')
             ).move(580, 0).scale(0.009),
       Panel(
             SVG(os.path.join(results_folder, "diagrams", str(run_folder), "cle_time_profile-transfer_function.svg")),
             Text("(C)", 25, 20, size=18, weight='bold')
            ).move(1160, 0).scale(0.009),
        ).save(os.path.join(figure_path, exp_name + "--cle_profiler.svg"))

os.system("inkscape " + os.path.join(figure_path, exp_name + "--cle_profiler.svg")
          + " --export-png=" + os.path.join(figure_path_png, exp_name + "--cle_profiler.png")
          + " --export-dpi=600")

## =============================================================================
# brain to robot ratio

copyfile(os.path.join(results_folder, "diagrams/braintorobot_ratio.svg"),
          os.path.join(figure_path, exp_name
                       + '--braintorobot_ratio.svg'))

copyfile(os.path.join(results_folder, "diagrams/nodehours.svg"),
          os.path.join(figure_path, exp_name
                       + '--nodehours.svg'))
