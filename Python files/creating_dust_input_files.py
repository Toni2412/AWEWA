from processing_awebox_file import process_file
from concatenating_data_several_rotations import create_trajectory_and_orientation_files
from creating_dust_pre_in import create_or_change_dust_pre_in
from creating_references_in import create_or_change_references_in
from creating_dust_in_panels import create_or_change_dust_in_panels
from creating_dust_in_particles import create_or_change_dust_in_particles, calculate_octree_parameters
from creating_dust_post_in import create_or_change_dust_post_in
import numpy as np




def average_time_step(lst):
    return np.average(np.diff(lst))





def create_dust_files(n_rot, res, file_path_awebox, folder_path, single_or_dual, apply_pitch_correction, CL0, alpha_max, alpha_min, particles_or_panels, box_length):

    """
    Creates the .dat files for the trajectory and angles and modifies the DUST input files to fit the trajectory.
    Args:
        n_rot (int): Number of rotations to simulate (in case of dual kites, this is the number of half rotations, 
                   in case of single kites, this is the number of full rotations).
        res (int): Resolution for the data. If res=1, all data is used; if res=2, every second data point is used...
                   This is useful to reduce the time of the simulation.
        file_path_awebox (str): Path to the CSV file containing the data.
        folder_path (str): Path to the output directory where the .dat files will be saved.
        single_or_dual (str): "single" for single wing, "dual" for dual wing configuration.
        apply_pitch_correction (bool): Whether to apply pitch correction.
        CL0 (float): Lift coefficient at zero angle of attack.(deduce from 3D drag curve)
        alpha_max (float): Maximum angle of attack in degrees.(deduce from 3D lift curve)
        alpha_min (float): Minimum angle of attack in degrees.(deduce from 3D lift curve)
        particles_or_panels (str): "particles" for particle-based simulation, "panels" for panel-based simulation.
        box_length (float): Length of one side of the cubic simulation box (only for particle-based simulation).
    Returns:
        None, creates or modifies the necessary files in the specified folder.
    """

    # Process the AWEBOX file to extract necessary data
    u_inf, rho_inf, _, _, _ = process_file(file_path_awebox, single_or_dual, apply_pitch_correction, CL0, alpha_max, alpha_min)
    # concatenate the data for multiple rotations and apply the specified resolution
    time_mult_rot, trajectories_mult_rot, _  = create_trajectory_and_orientation_files(single_or_dual, n_rot, res, file_path_awebox, folder_path, apply_pitch_correction, CL0, alpha_max, alpha_min)

    # Define the origins for the references.in file based on the first position of each trajectory
    origins = [f"(/{trajectory[0, 0]:.2f}, {trajectory[0, 1]:.2f}, {trajectory[0, 2]:.2f}/)" for trajectory in trajectories_mult_rot]

    # Create or modify the files dust_pre.in and references.in
    create_or_change_dust_pre_in(folder_path, single_or_dual)
    create_or_change_references_in(folder_path, single_or_dual, origins)

    # Calculate simulation parameters
    N_sim_steps = len(time_mult_rot)
    t_start = time_mult_rot[0]
    t_end = time_mult_rot[len(time_mult_rot)-1]
    t_end_formatted = f"{t_end:.8f}"
    dt = average_time_step(time_mult_rot)
    dt_formatted = f"{dt:.8f}"
    u_inf_formatted = f"{u_inf:.5}"

    # Create or modify the file dust.in
    if particles_or_panels == "particles":                     
        particles_box_min, particles_box_max, n_box  = calculate_octree_parameters(file_path_awebox, single_or_dual, t_end, int(box_length/2))
        create_or_change_dust_in_particles(folder_path, t_start, t_end_formatted, dt, u_inf, particles_box_min, particles_box_max, n_box, box_length)
    elif particles_or_panels == "panels":
        create_or_change_dust_in_panels(folder_path, t_start, t_end_formatted, dt_formatted, u_inf_formatted, rho_inf)

    # Create or modify the file dust_post.in
    create_or_change_dust_post_in(folder_path, 1, N_sim_steps, 1, file_path_awebox, t_end, single_or_dual)
