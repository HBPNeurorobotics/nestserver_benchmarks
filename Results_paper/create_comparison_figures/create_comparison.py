#!/usr/bin/env python
#coding=utf-8

from svgutils.compose import *

Figure("16cm", "9cm",
       Panel(
             SVG("white.svg"),
            ).scale(0.12),
        Panel(
              SVG("white.svg"),
              Text("HPC Benchmark", 25, 20, size=12, weight='bold')
             ).move(50, 0).scale(0.02),
        Panel(
              SVG("white.svg"),
              Text("Embodied Rodent Motor Cortex", 25, 20, size=12, weight='bold')
             ).move(280, 0).scale(0.02),
        Panel(
              SVG("white.svg"),
              Text("Embodied Rodent Multi-Region Brain", 25, 20, size=12, weight='bold')
             ).move(516, 0).scale(0.02),
        Panel(
              SVG("input/hpc--braintorobot_ratio.svg"),
              Text("(A)", 25, 20, size=18, weight='bold')
             ).move(0, 80).scale(0.009),
        Panel(
              SVG("input/smallbrain--braintorobot_ratio.svg"),
              Text("(B)", 25, 20, size=18, weight='bold')
             ).move(600, 80).scale(0.009),
        Panel(
              SVG("input/fullbrain--braintorobot_ratio.svg"),
              Text("(C)", 25, 20, size=18, weight='bold')
             ).move(1200, 80).scale(0.009),
        Panel(
              SVG("input/hpc--nodehours.svg"),
              Text("(D)", 25, 20, size=18, weight='bold')
             ).move(0, 550).scale(0.009),
        Panel(
              SVG("input/smallbrain--nodehours.svg"),
              Text("(E)", 25, 20, size=18, weight='bold')
             ).move(600, 550).scale(0.009),
        Panel(
              SVG("input/fullbrain--nodehours.svg"),
              Text("(F)", 25, 20, size=18, weight='bold')
             ).move(1200, 550).scale(0.009)
        ).save("output/benchmark_comparison.svg")


os.system("inkscape output/benchmark_comparison.svg --export-png=output/benchmark_comparison.png --export-dpi=600")
