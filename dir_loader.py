import os
import argparse
import subprocess

def dir(input_path):
    files = os.listdir(input_path)
    files = [i for i in files if i.lower().endswith(('.obj'))]
    print(f"\n{len(files)} meshes found.\n")
    print(files)
    return files

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description="Script for registering SMPL model to meshes in a folder.")

# Define command-line arguments
parser.add_argument("--input", "-i", help="Path to folder containing input meshes.", required=True)
parser.add_argument("--output", "-o", help="Path to save output meshes.", required=True)
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

meshes = dir(input_path)
main_script = "./smpl_reg.py"

for j in meshes:

    mesh_path = os.path.join(input_path,j)
    save_path = os.path.join(output_path,os.path.splitext(j)[0])
    os.mkdir(save_path)
    command = f"python {main_script} --input {mesh_path} --output {save_path} --texture {texture} --gender {gender} --verbose"

    # Run mesh transformations script
    try:
        subprocess.run([command], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {main_script}: {e}")

print("\nSMPL has been registered to all the meshes.\n")
