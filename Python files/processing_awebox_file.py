import numpy as np # type: ignore
import pandas as pd # type: ignore


def vector_rotation(e, v, theta):

    e_rot = e * np.cos(theta) + np.cross(v, e) * np.sin(theta) + v * np.dot(v, e) * (1 - np.cos(theta))

    return e_rot



def pitch_correction(R_vec, theta):

    R = np.array(R_vec).reshape(3, 3).T
    ex = R[:,0]
    ey = R[:,1]
    ez = R[:,2]

    ex_rot = vector_rotation(ex, ey, theta)
    ey_rot = vector_rotation(ey, ey, theta)
    ez_rot = vector_rotation(ez, ey, theta)

    R_rotated = np.vstack((
        ex_rot, ey_rot, ez_rot
    )).T.reshape(9,)

    return R_rotated



def process_file(file_path, single_or_dual, apply_pitch_correction, CL0, alpha_max, alpha_min):

    """ Process the CSV file to extract all relevant data. 
        Applies pitch correction. This is neccesary to exactly match the 3D lift and drag curves of the wings used in awebox and DUST.
    Args:
        file_path (str): Path to the CSV file.
        single_or_dual (str): "single" for single wing, "dual" for dual wing configuration.
        apply_pitch_correction (bool): Whether to apply pitch correction.
        CL0 (float): Lift coefficient at zero angle of attack.(deduce from 3D drag curve)
        alpha_max (float): Maximum angle of attack in degrees.(deduce from 3D lift curve)
        alpha_min (float): Minimum angle of attack in degrees.(deduce from 3D lift curve)     
    Returns:
        tuple: A tuple containing:
            - u_inf (float): Average wind speed.
            - rho_inf (float): Average air density.
            - time (np.ndarray): Time array.
            - trajectories (list): List of np.ndarrays containing the trajectories of the wings.(just one for single, two for dual)
            - orientations (list): List of np.ndarrays containing the orientations of the wings.(just one for single, two for dual)
    """

    # Initialize lists to store data
    trajectories = []
    orientations = []
    ll_u_inf = []
    ll_rho_inf = []

    # Read the CSV file and extract time column
    df = pd.read_csv(file_path)
    time = df["time"].to_numpy()

    # Determine indices based on single or dual wing configuration
    if single_or_dual == "single":
        ll_indices = [1]
        node = 0
    elif single_or_dual == "dual":
        ll_indices = [2, 3]
        node = 1

    # Loop through each wing index to extract relevant data
    for i in ll_indices:
        ll_u_inf.append(df[f"outputs_aerodynamics_u_infty{i}_0"])
        ll_rho_inf.append(df[f"outputs_aerodynamics_air_density{i}_0"])
        trajectories.append(np.column_stack((df[f"x_q{i}{node}_0"], df[f"x_q{i}{node}_1"], df[f"x_q{i}{node}_2"])))

        orientation = (np.column_stack((
            df[f"outputs_aerodynamics_ehat_chord{i}_0"],
            df[f"outputs_aerodynamics_ehat_chord{i}_1"],
            df[f"outputs_aerodynamics_ehat_chord{i}_2"],
            df[f"outputs_aerodynamics_ehat_span{i}_0"],
            df[f"outputs_aerodynamics_ehat_span{i}_1"],
            df[f"outputs_aerodynamics_ehat_span{i}_2"],
            df[f"outputs_aerodynamics_ehat_up{i}_0"],
            df[f"outputs_aerodynamics_ehat_up{i}_1"],
            df[f"outputs_aerodynamics_ehat_up{i}_2"])))
        
        if apply_pitch_correction == False:
            orientations.append(orientation)
        
        elif apply_pitch_correction == True:
            lift_coefficient = df[f'x_coeff{i}{node}_0']
            CL_pr = 1 / (np.deg2rad(alpha_max - alpha_min))
            alpha = [(lift_coefficient[k] - CL0) / CL_pr for k in range(len(lift_coefficient))]
    
            orientation_corrected = np.array([
                pitch_correction(orientation[k, :], alpha[k]) for k in range(len(alpha))
            ])
            
            orientations.append(orientation_corrected)

    u_inf = np.mean(ll_u_inf)
    rho_inf = np.mean(ll_rho_inf)

    return u_inf, rho_inf, time, trajectories, orientations