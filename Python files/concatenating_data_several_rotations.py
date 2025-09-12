import numpy as np # type: ignore
from scipy.spatial.transform import Rotation as R # type: ignore
from processing_awebox_file import process_file



def compute_euler_angles(orientation):

    R_matrix = np.array(orientation).reshape(3, 3)
    euler_angles = R.from_matrix(R_matrix).as_euler('ZXZ')

    return tuple(euler_angles)




def concatenate_time(n,time_list):

    concatenated_time_list = time_list

    if n == 1:
        return concatenated_time_list
    else:
        for i in range(1,n):
            concatenated_time_list = np.concatenate((concatenated_time_list, time_list[1:] + i * time_list[-1]), axis=0)

        return concatenated_time_list
    



def concatenate_data_periodic(n, data):

    concatenated_data = data
    if n == 1:
        return concatenated_data
    else:
        for i in range(1,n):
            concatenated_data = np.concatenate((concatenated_data, data[1:]), axis=0)

        return np.array(concatenated_data)
    



def concatenate_data_semiperiodic(n, data_1, data_2):

    result = []
    result.extend(data_1)
    for i in range(1,n):
        if i % 2 == 0:
            result.extend(data_1[1:])
        else:
            result.extend(data_2[1:])

    return np.array(result)




def create_trajectory_and_orientation_files(single_or_dual, n_rot, res, file_path, folder_path, apply_pitch_correction, CL0, alpha_max, alpha_min):
    """
    Create trajectory and orientation files for multiple rotations. Computes Euler angles from orientation matrices and saves the data to .dat files.

    Args:
        single_or_dual (str): "single" for single wing, "dual" for dual wing configuration.
        n_rot (int): Number of rotations.
        res (int): Resolution for the data. If res=1, all data is used; if res=2, every second data point is used...
                   This is useful to reduce the time of the simulation.
        file_path (str): Path to the CSV file containing the data.
        folder_path (str): Path to the output directory where the .dat files will be saved.
        apply_pitch_correction (bool): Whether to apply pitch correction.
        CL0 (float): Lift coefficient at zero angle of attack.(deduce from 3D drag curve)
        alpha_max (float): Maximum angle of attack in degrees.(deduce from 3D lift curve)
        alpha_min (float): Minimum angle of attack in degrees.(deduce from 3D lift curve)
     
    Returns:
        saves the data to .dat files and returns the time, and lists containing the trajectories and Euler angles of the wing(s).
    """

    u_inf, rho_inf, time, trajectories, orientations = process_file(file_path, single_or_dual, apply_pitch_correction, CL0, alpha_max, alpha_min) 
    
    trajectories_mult_rot = []
    time_mult_rot = concatenate_time(n_rot, time)[::res]

    # Compute Euler angles and concatenate data based on single or dual wing configuration
    if single_or_dual == "single":

        ll_names = ["first_wing"]
        trajectories_mult_rot.append(concatenate_data_periodic(n_rot, trajectories[0])[::res])

        euler_angles = [compute_euler_angles(orientation) for orientation in orientations[0]]

        euler_angles_mult_rot = concatenate_data_periodic(n_rot,euler_angles)[::res]
        euler_angles_mult_rot = [np.column_stack([np.unwrap(euler_angles_mult_rot[:, i]) for i in range(3)])]

    elif single_or_dual == "dual":  

        ll_names = ["first_wing", "second_wing"]
        trajectories_mult_rot = [concatenate_data_semiperiodic(n_rot, trajectories[0], trajectories[1])[::res], concatenate_data_semiperiodic(n_rot, trajectories[1], trajectories[0])[::res]]

        first_wing_euler_angles = [compute_euler_angles(orientation) for orientation in orientations[0]]
        second_wing_euler_angles = [compute_euler_angles(orientation) for orientation in orientations[1]]

        first_wing_euler_angles_mult_rot = (concatenate_data_semiperiodic(n_rot, first_wing_euler_angles, second_wing_euler_angles)[::res])
        second_wing_euler_angles_mult_rot = (concatenate_data_semiperiodic(n_rot, second_wing_euler_angles, first_wing_euler_angles)[::res])

        first_wing_euler_angles_mult_rot = np.column_stack([np.unwrap(first_wing_euler_angles_mult_rot[:, i]) for i in range(3)])
        second_wing_euler_angles_mult_rot = np.column_stack([np.unwrap(second_wing_euler_angles_mult_rot[:, i]) for i in range(3)])  

        euler_angles_mult_rot = [first_wing_euler_angles_mult_rot, second_wing_euler_angles_mult_rot]

    for i, name in enumerate(ll_names):
        # save trajectory data in .dat file with time in the specified folder
        trajectory_data = np.column_stack((time_mult_rot, np.array(trajectories_mult_rot[i])))
        np.savetxt(f"{folder_path}/{name}_trajectory.dat", trajectory_data, delimiter="\t", fmt="%.8f")

        for name, angles in zip(ll_names, euler_angles_mult_rot):
            for angle_name, i in zip(["Z1", "X", "Z2"], range(3)):
                np.savetxt(f"{folder_path}/{name}_euler_angle_{angle_name}.dat", np.column_stack((time_mult_rot, np.unwrap(np.array(angles)[:, i]))), delimiter="\t", fmt="%.8f")


    return time_mult_rot, trajectories_mult_rot, euler_angles_mult_rot
