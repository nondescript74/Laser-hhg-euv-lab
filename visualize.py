#!/usr/bin/env python3
"""Run the EUV lithography simulation and open an interactive visualization."""

import argparse
import numpy as np
from backend.lithography_model import VirtualLithoProcess
from backend.visualization import build_pipeline_figure


def make_aerial_image(nx=256, ny=256):
    """Default 20nm vertical line target (matches /api/simulate)."""
    ai = np.zeros((nx, ny))
    center = ny // 2
    ai[:, center - 10:center + 10] = 1.0
    return ai


def main():
    parser = argparse.ArgumentParser(description="EUV Litho Pipeline Visualizer")
    parser.add_argument("--dose", type=float, default=20.0)
    parser.add_argument("--peb-time", type=float, default=60.0)
    parser.add_argument("--diffusion-coef", type=float, default=5.0)
    parser.add_argument("--k-amp", type=float, default=0.2)
    parser.add_argument("--r-max", type=float, default=100.0)
    parser.add_argument("--r-min", type=float, default=0.1)
    parser.add_argument("--n-mack", type=int, default=5)
    parser.add_argument("--grid", type=int, default=256, help="Grid size NxN")
    parser.add_argument("--no-browser", action="store_true", help="Save HTML instead of opening browser")
    args = parser.parse_args()

    model = VirtualLithoProcess(nx=args.grid, ny=args.grid)
    ai = make_aerial_image(args.grid, args.grid)

    params = {
        "dose": args.dose, "peb_time": args.peb_time,
        "diffusion_coef": args.diffusion_coef, "k_amp": args.k_amp,
        "r_max": args.r_max, "r_min": args.r_min, "n_mack": args.n_mack,
    }

    stages = model.simulate_chain_detailed(ai, params)
    fig = build_pipeline_figure(stages, title=f"EUV Litho Pipeline (dose={args.dose} mJ/cm\u00b2)")

    if args.no_browser:
        fig.write_html("litho_visualization.html")
        print("Saved to litho_visualization.html")
    else:
        fig.show()


if __name__ == "__main__":
    main()
