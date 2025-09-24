from processing_awebox_file import *
from concatenating_data_several_rotations import * 
from creating_flowfield_analysis import * 
import os
import subprocess
import pyvista as pv

def velocity_in_front_of_kite(n_rot, res, file_path_awebox, folder_path, single_or_dual, apply_pitch_correction, CL0, alpha_max, alpha_min, d): 

    """
    Calculates the velocity a distance d in front of each wing over the entire trajectory.
    Returns the velocity in front of the wing(s) as numpy array(s).
    Args: 
        n_rot (int): Number of rotations in the trajectory. (has to be either the same as in the dust simulation step or a lower number if you only want to look at the first rotations)
        res (int): Resolution of the trajectory. (has to be either the same as in the dust simulation step or a higher number if you want a less resolved result)
        file_path_awebox (str): Path to the input trajectory file.
        folder_path (str): Path to the folder where the DUST files are located.
        single_or_dual (str): Whether the trajectory is for a single kite or dual kite system. Options are "single" or "dual".
        apply_pitch_correction (bool): Whether to apply pitch correction to the trajectory.
        CL0 (float): Lift coefficient at 0 angle of attack.
        alpha_max (float): Maximum angle of attack.
        alpha_min (float): Minimum angle of attack. (has to be the same as )
        d (float): Distance in front of the wing to evaluate the velocity. This is the distance (in meters) along the wing's chord direction at a given timestep

    Returns:
        tuple: A tuple containing one or two arrays with the velocity (x,y,z component) in front of the respective wing at each timestep.
    """


    _, _, time, trajectories, orientations = process_file(file_path_awebox, single_or_dual, apply_pitch_correction, CL0, alpha_max, alpha_min)

    time_mult_rot = concatenate_time(n_rot, time)[::res]
    trajectories_mult_rot = []
    orientations_mult_rot = []

    if single_or_dual == "single":
        trajectories_mult_rot.append(concatenate_data_periodic(n_rot, trajectories[0])[::res])
        orientations_mult_rot.append(concatenate_data_periodic(n_rot, orientations[0])[::res])
        ll_names = ["first_wing"]
    elif single_or_dual == "dual":
        trajectories_mult_rot = [concatenate_data_semiperiodic(n_rot, trajectories[0], trajectories[1])[::res], concatenate_data_semiperiodic(n_rot, trajectories[1], trajectories[0])[::res]]
        orientations_mult_rot = [concatenate_data_semiperiodic(n_rot, orientations[0], orientations[1])[::res], concatenate_data_semiperiodic(n_rot, orientations[1], orientations[0])[::res]]
        ll_names = ["first_wing", "second_wing"]

    # creating dust_post.in file for the velocity evaluation
    n_xyz_point =  "(/1,1,1/)"
    output_folder = os.path.join(folder_path, f"Postprocessing/velocity_{d}m_in_front")
    os.makedirs(output_folder, exist_ok=True)

    file_path = f"{folder_path}/dust_post.in"
    first_block = f"""
    basename = Postprocessing/velocity_{d}m_in_front/post
    data_basename = Output/flapwing

    """

    with open(file_path, 'w') as file:
        file.write(first_block)

    for orientation, trajectory, name in zip(orientations_mult_rot, trajectories_mult_rot, ll_names):

        for i in range(0, len(time_mult_rot), 1):

            evaluation_point = np.round([
                trajectory[i][0] - d* orientation[i][0],
                trajectory[i][1] - d* orientation[i][3],
                trajectory[i][2] - d* orientation[i][6]
            ], 3)

            evaluation_point_formatted = f"(/{evaluation_point[0]}, {evaluation_point[1]}, {evaluation_point[2]}/)"

            create_or_change_flow_field_analysis(folder_path, i+1, i+1, n_xyz_point, evaluation_point_formatted, evaluation_point_formatted , f"flow_in_front_{name}_{i+1}")

    # running dust_post to create the velocity files
    subprocess.run("dust_post", cwd=folder_path, shell=True)

    ll_results = []
    for name in ll_names: 
        ll_results_1 = []
        for i in range(1, len(time_mult_rot)+1, 1):
            if i<10: 
                point = os.path.join(folder_path, f"Postprocessing/velocity_{d}m_in_front/post_flow_in_front_{name}_{i}_000{i}.vtr")

            elif i<100: 
                point = os.path.join(folder_path, f"Postprocessing/velocity_{d}m_in_front/post_flow_in_front_{name}_{i}_00{i}.vtr")

            else: 
                point = os.path.join(folder_path, f"Postprocessing/velocity_{d}m_in_front/post_flow_in_front_{name}_{i}_0{i}.vtr")

            ll_results_1.append(np.array(pv.read(point)["velocity"][0]))
        ll_results.append(ll_results_1)

    return ll_results, time_mult_rot