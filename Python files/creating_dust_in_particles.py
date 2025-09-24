import pandas as pd
import numpy as np
import os




ceil_to_nearest = lambda x, d: int(np.ceil(x / d)) * d

def calculate_octree_parameters(file_path_awebox, single_or_dual, t_end, d):

    df = pd.read_csv(file_path_awebox)

    if single_or_dual == "single":
        
        u_inf_max  = np.max(df["outputs_aerodynamics_u_infty1_0"])

        x_max = ceil_to_nearest(df["x_q10_0"].max() + d + t_end * u_inf_max, d)
        x_min = ceil_to_nearest(df["x_q10_0"].min() - d, d)

        y_max = ceil_to_nearest(df["x_q10_1"].max() + 4*d, d)
        y_min = ceil_to_nearest(df["x_q10_1"].min() - 5*d, d)

        z_max = ceil_to_nearest(df["x_q10_2"].max() + 4*d, d)
        z_min = ceil_to_nearest(df["x_q10_2"].min() - 4*d, d)

    elif single_or_dual == "dual":

        u_inf_max  = np.max(df["outputs_aerodynamics_u_infty2_0"])

        x_max = ceil_to_nearest(max(df["x_q21_0"].max(), df["x_q31_0"].max()) + d + t_end * u_inf_max, d)
        x_min = ceil_to_nearest(min(df["x_q21_0"].min(), df["x_q31_0"].min()) - d, d)

        y_max = ceil_to_nearest(max(df["x_q21_1"].max(), df["x_q31_1"].max()) + 4*d, d)
        y_min = ceil_to_nearest(min(df["x_q21_1"].min(), df["x_q31_1"].min()) - 5*d, d)

        z_max = ceil_to_nearest(max(df["x_q21_2"].max(), df["x_q31_2"].max()) + 4*d, d)
        z_min = ceil_to_nearest(min(df["x_q21_2"].min(), df["x_q31_2"].min()) - 4*d, d)

    dx = int((x_max - x_min)/d)
    dy = int((y_max - y_min)/d)
    dz = int((z_max - z_min)/d)

    min_xyz = f"(/{x_min}, {y_min}, {z_min}/)"
    max_xyz = f"(/{x_max}, {y_max}, {z_max}/)"
    n_box = f"(/{dx}, {dy}, {dz}/)"

    return (min_xyz, max_xyz, n_box)





def create_or_change_dust_in_particles(folder_path_DUST_files, t_start, t_end, dt, u_inf, particles_box_min, particles_box_max, n_box, box_length): 

    file_path = f"{folder_path_DUST_files}/dust.in"

    new_content = f"""

basename       = ./Output/flapwing

! --- Time parameters ---
tstart = {t_start}
tend = {t_end}
dt = {dt}
dt_out = {dt}
output_start = T
! ndt_update_wake = 1

! --- Restart ---
restart_from_file = F

! --- Geometry files ---
geometry_file = geo_input.h5
reference_file = References.in

! --- stream parameters ---
u_inf = (/ {u_inf}, 0.0, 0.0 /)

! wake parameters  -------------
n_wake_panels = 2
n_wake_particles = 20000000

! wake regularisation ------------
divergence_filtering = T
filter_time_scale = 20
doublet_threshold = 0.01
rankine_rad = 0.12
vortex_rad = 0.12
cutoff_rad = 0.01

! Model parameters -------------------
particles_box_min = {particles_box_min}
particles_box_max = {particles_box_max}
fmm = T

! octree parameters--------------------
box_length = {box_length}
n_box = {n_box} ! number of octree boxes in each direction, e.g. (20, 20, 20)
octree_origin = {particles_box_min}
n_octree_levels = 4 ! subdivision of octree cubes, reduce to make faster
min_octree_part = 5 ! if a subdivision contains less particles that that, dust stops further divisions
multipole_degree = 2 
vortstretch = T
diffusion = T


! --- Lifting Lines parameters ---
ll_solver = GammaMethod
ll_reynolds_corrections = F
ll_max_iter = 100
ll_tol = 1.0e-4
ll_damp = 20
ll_loads_avl = F 

"""

    # Check if the file exists and compare the content
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            existing_content = file.read()

        # Update the file only if the content is different
        if existing_content != new_content:
            with open(file_path, 'w') as file:
                file.write(new_content)
    else:
        # Create the file and write the new content
        with open(file_path, 'w') as file:
            file.write(new_content)