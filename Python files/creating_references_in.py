import os




def create_reference_system(ref_tags_lst, files_lst, origin): 

    content = f"""
reference_tag = {ref_tags_lst[0]}
parent_tag = 0
origin = {origin}
orientation = (/1.0,0.0,0.0, 0.0,1.0,0.0, 0.0,0.0,1.0/)
multiple = F 
moving = T
motion = {{
pole = {{
input = position
input_type = from_file
file = {files_lst[0]}
}}
rotation = {{
input = position
input_type = simple_function
function = 0
Axis = (/ 1.0 , 0.0 , 0.0 /)
amplitude = 0.0
}}
}} 

reference_tag = {ref_tags_lst[1]}
parent_tag = {ref_tags_lst[0]} ! 0 : absolute reference frame
origin = (/0.,0.,0./)
orientation = (/1.0,0.0,0.0, 0.0,1.0,0.0, 0.0,0.0,1.0/)
multiple = F 
moving = T
motion = {{
pole = {{
input = position
input_type = simple_function
function = (/ 0 , 0 , 0 /)
amplitude = 0.00
}}
rotation = {{
input = position
input_type = from_file
file = {files_lst[1]}
Axis = (/ 0.0 , 0.0 , 1.0 /)
}}
}} 

reference_tag = {ref_tags_lst[2]}
parent_tag = {ref_tags_lst[1]} ! 0 : absolute reference frame! 
origin = (/0.,0.,0./)
orientation = (/1.0,0.0,0.0, 0.0,1.0,0.0, 0.0,0.0,1.0/)
multiple = F 
moving = T
motion = {{
pole = {{
input = position
input_type = simple_function
function = (/ 0 , 0 , 0 /)
amplitude = 0.00
}}
rotation = {{
input = position
input_type = from_file
file = {files_lst[2]}
Axis = (/ 1.0 , 0.0 , 0.0 /)
}}
}} 

reference_tag = {ref_tags_lst[3]}
parent_tag = {ref_tags_lst[2]} ! 0 : absolute reference frame
origin = (/0.,0.,0./)
orientation = (/1.0,0.0,0.0, 0.0,1.0,0.0, 0.0,0.0,1.0/)
multiple = F 
moving = T
motion = {{
pole = {{
input = position
input_type = simple_function
function = (/ 0 , 0 , 0 /)
amplitude = 0.00
}}
rotation = {{
input = position
input_type = from_file
file = {files_lst[3]}
Axis = (/ 0.0 , 0.0 , 1.0 /)
}}
}} 

reference_tag = {ref_tags_lst[4]}
parent_tag = {ref_tags_lst[3]} ! 0 : absolute reference frame
origin = (/0.,0.,0./)
orientation = (/1.0,0.0,0.0, 0.0,1.0,0.0, 0.0,0.0,1.0/)
multiple = F 
moving = F
"""
    
    return content
def create_or_change_references_in(folder_path, single_or_dual, origins): 
    
    file_path = f"{folder_path}/References.in"

    ref_tags_first_wing = ["first_trajectory", "first_wing_euler_angle_Z1", "first_wing_euler_angle_X", "first_wing_euler_angle_Z2", "first_wing"]
    ref_tags_second_wing = ["second_trajectory", "second_wing_euler_angle_Z1", "second_wing_euler_angle_X", "second_wing_euler_angle_Z2", "second_wing"]

    files_first_wing = [ "first_wing_trajectory.dat", "first_wing_euler_angle_Z1.dat", "first_wing_euler_angle_X.dat", "first_wing_euler_angle_Z2.dat" ]
    files_second_wing = [ "second_wing_trajectory.dat", "second_wing_euler_angle_Z1.dat", "second_wing_euler_angle_X.dat", "second_wing_euler_angle_Z2.dat"]

    if single_or_dual == "single":
        content = create_reference_system(ref_tags_first_wing, files_first_wing, origins[0])

    elif single_or_dual == "dual":

        content_first = create_reference_system(ref_tags_first_wing, files_first_wing, origins[0])
        content_second = create_reference_system(ref_tags_second_wing, files_second_wing, origins[1])
        content = content_first + "\n" + content_second

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
