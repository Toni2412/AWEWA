


def create_or_change_wake_visualization(folder_path, start_res, end_res, step_res):
    """
    Removes the current visualization block if it exists and adds the new one.
    If no wake visualization block exists, it simply adds the new one.

    Args:
        folder_path (str): Path to the folder where the dust_post.in file is located.
        start_res (int): The simulation step at which you want to start the flow field analysis.
        end_res (int): The simulation step at which you want to end the flow field analysis.

    Returns:
        None: Creates or modifies the wake visualization block in the dust_post.in file.
    """

    file_path = f"{folder_path}/dust_post.in"
    wake_vis_block = f"""analysis = {{
  name = v1
  type = Viz

  format = vtk

  start_res = {start_res}
  end_res = {end_res}
  step_res = {step_res}
  wake = T

  variable = Vorticity

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
        if f"type = Viz" in existing_block:
            content = content.replace(existing_block, "")
        analysis_start = content.find("analysis = {", analysis_start + 1)

    # Add the new flow_field analysis block
    content += "\n" + wake_vis_block

    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.write(content)