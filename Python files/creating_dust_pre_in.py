import os




def create_or_change_dust_pre_in(folder_path, single_or_dual):
    """
    Creates or modifies the dust_pre.in file in the specified folder.
    
    Args:
        folder_path (str): Path to the folder where the dust_pre.in file will be created or modified.
        single_or_dual (str): Specifies whether to create a single or dual system.

    Returns:
        None: Creates or modifies the dust_pre.in file in the specified folder.
    """
    file_path = f"{folder_path}/dust_pre.in"

    if single_or_dual == "single":
        content = """

comp_name = first_wing
geo_file = ParamWing.in
ref_tag = first_wing

file_name = geo_input.h5 
        """
    elif single_or_dual == "dual":
        content = """
comp_name = first_wing
geo_file = ParamWing.in
ref_tag = first_wing

comp_name = second_wing
geo_file = ParamWing.in
ref_tag = second_wing

file_name = geo_input.h5 
        """
    # Check if the file exists and compare the content
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            existing_content = file.read()

        # Update the file only if the content is different
        if existing_content != content:
            with open(file_path, 'w') as file:
                file.write(content)
    else:
        # Create the file and write the new content
        with open(file_path, 'w') as file:
            file.write(content)