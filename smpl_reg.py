"""
Script developed for

Image and Video Computing Group at the University of Colorado Boulder, USA and
Thomas Lab at the University of Colorado Anschutz Medical Campus, USA.

Author - Atharva R. Peshkar.

Command to run this script

python main.py --input <input mesh path> --output <output mesh path> --texture <texture path> --gender <male/female> --verbose

"""

import sys
import argparse
import subprocess
import os

# Paths to scripts used for preparing scans for registration.
multi_view_rendering = "./utils/keypoints_3d_estimation/01_render_multiview.py"
pose_pred_2D = "./utils/keypoints_3d_estimation/02_predict_2d_pose.py"
lift_2D_3D = "./utils/keypoints_3d_estimation/03_lift_keypoints.py"

# SMPL registration script
smpl_reg = "./smpl_registration/fit_SMPLH.py"

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description="Script for transforming, UV unwrapping, and applying texture to a mesh using Blender.")

# Define command-line arguments
parser.add_argument("--input", "-i", help="Input mesh path", required=True)
parser.add_argument("--output", "-o", help="Output mesh path", required=True)
parser.add_argument("--texture", "-t", help="Texture path", required=True)
parser.add_argument("--gender", "-g", help="Gender - female/male", required=False)
parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose mode")

# Parse the command-line arguments
args = parser.parse_args()

# Access the values of the arguments
input_path = args.input
output_path = args.output
texture = args.texture
gender = args.gender
verbose = args.verbose

# Files and folders required for preparing scans.
renders_folder = f"{os.path.join(output_path,os.path.splitext(os.path.basename(input_path))[0])}_renders"
pose_2D_json = os.path.join(output_path,"2D_pose.json")
pose_3D_json = os.path.join(output_path,"3D_pose.json")
p3d_render_data = os.path.join(renders_folder,"p3d_render_data.pkl")

# Commands to prepare the scans.
multi_view_rendering_comm = f"python {multi_view_rendering} {input_path} -t {texture} -r {output_path}"
pose_pred_2D_comm = f"python {pose_pred_2D} {renders_folder} -r {output_path} -v"
lift_2D_3D_comm = f"python {lift_2D_3D} {input_path} -k2 {pose_2D_json} -r {pose_3D_json} -cam {p3d_render_data} -c ./config.yml"

# Command for SMPL registration
if(gender):
    smpl_reg_comm = f"python {smpl_reg} {input_path} {pose_3D_json} {output_path} -gender {str(gender).lower()} -hands"
else:
    smpl_reg_comm = f"python {smpl_reg} {input_path} {pose_3D_json} {output_path} -hands"

# Running the scripts to prepare the scans for registration.
# Run the 01_render_multiview.py script 
try:
    subprocess.run([multi_view_rendering_comm], shell=True, check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running {multi_view_rendering_comm}: {e}")

# Run 02_predict_2d_pose.py script
try:
    subprocess.run([pose_pred_2D_comm], shell=True, check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running {pose_pred_2D_comm}: {e}")

# Run 03_lift_keypoints.py script
try:
    subprocess.run([lift_2D_3D_comm], shell=True, check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running {lift_2D_3D_comm}: {e}")

# Run the SMPL-H Registration script.
try:
    subprocess.run([smpl_reg_comm], shell=True, check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running {smpl_reg_comm}: {e}")

print("\n *** SMPL registration is complete *** \n")