import numpy as np
import pandas as pd





def calculate_flowfield_parameters_kite_plane(file_path_awebox):
    """
    Calculate flowfield parameters including v_normal, x_max, x_min, y_max, y_min, z_max, and z_min.

    Args:
        file_path_awebox (str): Path to the CSV file containing the data.

    Returns:
        tuple: A tuple containing:
            - min_xyz (str): Minimum coordinates in the format "(x_min, y_min, z_min)".
            - max_xyz (str): Maximum coordinates in the format "(x_max, y_max, z_max)".
            - v_normal (np.ndarray): Normalized vector representing the elevation angle. (needed to calculate the component of the velocity/force that acts along the tether direction)

    """
    plot_dict = pd.read_csv(file_path_awebox)

    elevation_opt = np.arcsin(np.mean(plot_dict['x_q10_2']) / plot_dict['theta_l_t_0'][0])
    v_normal = [np.cos(elevation_opt), 0, np.sin(elevation_opt)]
    Roty = np.array([[np.cos(elevation_opt), 0, np.sin(elevation_opt)], 
                     [0, 1, 0], 
                     [-np.sin(elevation_opt), 0, np.cos(elevation_opt)]])

    eval_e1 = 0.5 * np.mean(plot_dict['x_q21_0']) + 0.5 * np.mean(plot_dict['x_q31_0'])
    eval_e3 = 0.5 * np.mean(plot_dict['x_q21_2']) + 0.5 * np.mean(plot_dict['x_q31_2'])
    eval_rot = np.dot(Roty, np.array([[eval_e1], [0], [eval_e3]])).squeeze()

    lims = [[-300, 300], [-300, 300]]
    resolution = 3
    evaluation_points_e1 = np.linspace(lims[0][0], lims[0][1], resolution)
    evaluation_points_e2 = np.linspace(lims[1][0], lims[1][1], resolution)

    pstns = []
    for ep_e1 in evaluation_points_e1:
        for ep_e2 in evaluation_points_e2:
            p_k = np.dot(Roty.T, np.array([[eval_rot[0]], [ep_e1], [ep_e2]]))
            pstns.append(p_k)

    pstns = np.array(pstns)
    x_max = np.round(np.max(pstns[:, 0]), 1)
    x_min = np.round(np.min(pstns[:, 0]), 1)
    y_max = np.round(np.max(pstns[:, 1]), 1)
    y_min = np.round(np.min(pstns[:, 1]), 1)
    z_max = np.round(np.max(pstns[:, 2]), 1)
    z_min = np.round(np.min(pstns[:, 2]), 1)

    min_xyz = f"(/{x_min}, {y_min}, {z_min}/)"
    max_xyz = f"(/{x_max}, {y_max}, {z_max}/)"


    return min_xyz, max_xyz, np.round(v_normal,3)





def calculate_flowfield_parameters_xz(file_path_awebox, t_end, single_or_dual):
    '''
    Args:
        file_path_awebox (str) : file path to CSV file containing the output data from the awebox simulation
        t_end (float) : end time of the simulation (to calculate how far the wake propagates)
        single_or_dual (str): "single" for single wing, "dual" for dual wing configuration.
    Returns: 
        The parameters that are neccesairy for the flowfield analysis. 
        min_xyz, max_xyz (str): the coordinates of the frame (in the format required by DUST)
        n_xyz (int): suggested resolutions for the x and z directions. Other values can of course also be used

    '''

    df = pd.read_csv(file_path_awebox)
    d = 60 # some margin around the trajectory, change if neccesary 

    if single_or_dual == "single":
        u_inf_max  = np.max(df["outputs_aerodynamics_u_infty1_0"])

        x_max = round(df["x_q10_0"].max() + d + t_end * u_inf_max, 1)
        x_min = round(df["x_q10_0"].min() - d, 1)

        z_max = round(df["x_q10_2"].max() + d, 1)
        z_min = round(df["x_q10_2"].min() - d, 1)
    
    elif single_or_dual == "dual":
        u_inf_max  = np.max(df["outputs_aerodynamics_u_infty2_0"])

        x_max = round(max(df["x_q21_0"].max(), df["x_q31_0"].max()) + d + t_end * u_inf_max, 1)
        x_min = round(min(df["x_q21_0"].min(), df["x_q31_0"].min()) - d, 1)

        z_max = round(max(df["x_q21_2"].max(), df["x_q31_2"].max()) + d, 1)
        z_min = round(min(df["x_q21_2"].min(), df["x_q31_2"].min()) - d, 1)

    # only works for trajectories that rotate around the y-axis
    min_xyz = f"(/{x_min}, {0}, {z_min}/)"
    max_xyz = f"(/{x_max}, {0}, {z_max}/)"


    n_x = int((x_max - x_min) / 5)
    n_z = int((z_max - z_min) / 5)

    n_xyz = f"(/{n_x}, 1, {n_z}/)"

    return min_xyz, max_xyz, n_xyz




def create_or_change_flow_field_analysis(folder_path, start_res, end_res, n_xyz, min_xyz, max_xyz, name ):
    """
    Removes the current flow_field analysis block if it exists and adds the new one.
    If no flow_field analysis block exists, it simply adds the new one.

    Args:
        folder_path (str): Path to the folder where the dust_post.in file is located.
        start_res (int): The simulation step at which you want to start the flow field analysis.
        end_res (int): The simulation step at which you want to end the flow field analysis.
        n_xyz (str): Number of points in the x, y, and z directions for the flow field analysis. Has to be in the format "(/1,1,1/)".
        min_xyz (str): Minimum coordinates for the flow field analysis. Has to be in the format "(/1,1,1/)".
        max_xyz (str): Maximum coordinates for the flow field analysis. Has to be in the format "(/1,1,1/)".

    Returns:
        None: Creates or modifies the flow field analysis in the dust_post.in file.
    """
    file_path = f"{folder_path}/dust_post.in"
    flow_analysis_block = f"""analysis = {{
  type = flow_field
  name = {name}

  start_res = {start_res}
  end_res = {end_res}
  step_res = 1

  format = vtk
  average = F
  
  variable = Velocity
  n_xyz = {n_xyz}
  min_xyz = {min_xyz}
  max_xyz = {max_xyz}
}}
"""

    # Read the file content
    with open(file_path, 'r') as file:
        content = file.read()

    # Remove any existing flow_field analysis block
    analysis_start = content.find("analysis = {")
    while analysis_start != -1:
        analysis_end = content.find("}", analysis_start) + 1
        existing_block = content[analysis_start:analysis_end]
        if f"name = {name}" in existing_block:
            content = content.replace(existing_block, "")
        analysis_start = content.find("analysis = {", analysis_start + 1)

    # Add the new flow_field analysis block
    content += "\n" + flow_analysis_block

    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.write(content)