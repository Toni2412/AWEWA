from creating_load_analysis import create_or_change_load_analysis_dual, create_or_change_load_analysis_single   
from creating_wake_visualization import create_or_change_wake_visualization
import os


def create_or_change_dust_post_in(folder_path, start_res, end_res, step_res, file_path_input_trajectory, t_end, single_or_dual):
    """
    Creates a dust_post.in file with the necessary analysis blocks for the simulation.
    
    Returns:
        None: Creates the dust_post.in file in the current working directory.
    """

    output_path = os.path.join(folder_path, "Postprocessing")
    os.makedirs(output_path, exist_ok=True)

    flow_field_resolution = 60  # TODO: integrate this into flow field parameter function
    loads_names = ["loads_first_wing", "loads_second_wing"]
    ll_data_names = ["sl01", "sl02"]
    components = reference_tags = ["first_wing", "second_wing"]

    file_path = f"{folder_path}/dust_post.in"

    first_block = """
basename = Postprocessing/post
data_basename = Output/flapwing
    
    """

    with open(file_path, 'w') as file:
        file.write(first_block)

    create_or_change_wake_visualization(folder_path, start_res, end_res, step_res)

    if single_or_dual == "dual":
        create_or_change_load_analysis_dual(folder_path, start_res, end_res, step_res, loads_names, components, reference_tags)


    elif single_or_dual == "single":
        create_or_change_load_analysis_single(folder_path, start_res, end_res, step_res, loads_names[0], components[0], reference_tags[0])

    
