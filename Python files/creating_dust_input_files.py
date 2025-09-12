from processing_awebox_file import process_file
from concatenating_data_several_rotations import create_trajectory_and_orientation_files
from creating_dust_pre_in import create_or_change_dust_pre_in
from creating_references_in import create_or_change_references_in
from creating_dust_in_panels import create_or_change_dust_in_panels
from creating_dust_post_in import create_or_change_dust_post_in
import numpy as np




def average_time_step(lst):
    return np.average(np.diff(lst))





def modify_dust_files(n_rot, res, file_path, folder_path, single_or_dual, particles_or_panels, apply_pitch_correction, CL0, alpha_max, alpha_min):

    """
    Creates the .dat files for the trajectory and angles and modifies the DUST input files to fit the trajectory.
    """

    u_inf, rho_inf, _, _, _ = process_file(file_path, single_or_dual, apply_pitch_correction, CL0, alpha_max, alpha_min)
    time_mult_rot, trajectories_mult_rot, euler_angles_mult_rot = create_trajectory_and_orientation_files(single_or_dual, n_rot, res, file_path, folder_path, apply_pitch_correction, CL0, alpha_max, alpha_min)

    origins = [f"(/{trajectory[0, 0]:.2f}, {trajectory[0, 1]:.2f}, {trajectory[0, 2]:.2f}/)" for trajectory in trajectories_mult_rot]

    create_or_change_dust_pre_in(folder_path, single_or_dual)
    create_or_change_references_in(folder_path, single_or_dual, origins)

    # makes the postprocessing fit the number of rotations and resulution chosen 
    N_sim_steps = len(time_mult_rot)
    t_start = time_mult_rot[0]
    t_end = time_mult_rot[len(time_mult_rot)-1]
    t_end_formatted = f"{t_end:.8f}"
    dt = average_time_step(time_mult_rot)
    dt_formatted = f"{dt:.8f}"
    box_length = 40
    u_inf_formatted = f"{u_inf:.5}"

    # if particles_or_panels == "particles":
    #     particles_box_min = calculate_octree_parameters(file_path, t_end, box_length)[0]
    #     particles_box_max = calculate_octree_parameters(file_path, t_end, box_length)[1]
    #     n_box = calculate_octree_parameters(file_path, t_end, box_length)[2]

    #     create_or_change_dust_in(folder_path, t_start, t_end_formatted, dt_formatted, u_inf_formatted, particles_box_min, particles_box_max, n_box, box_length, rho_inf)

    # elif particles_or_panels == "panels":
    create_or_change_dust_in_panels(folder_path, t_start, t_end_formatted, dt_formatted, u_inf_formatted, rho_inf)

    create_or_change_dust_post_in(folder_path, 1, N_sim_steps, 1, file_path, t_end, single_or_dual)
