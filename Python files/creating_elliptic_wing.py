import numpy as np # type: ignore
import os



def height_of_an_ellipse(A,a):
    """
    Calculate the height of an ellipse given the semi-major axis A and semi-minor axis a.
    
    Args:
        A (float): Area of the ellipse
        a (float): Half of the semi-major axis of the ellipse.
    
    Returns:
        float: Half of the semi-minoe axis of the ellipse.
    """
    return 2*A/(np.pi*a)




def create_elliptic_wing(folder_path, AR, span, N_elements, nelem_span, airfoil_profile, airfoil_table, end_chord):
    """
    Create an elliptic wing definition file for DUST.
    
    Args:
        folder_path (str): Path to the folder where the ParamWing.in file will be created.
        AR (float): Aspect ratio of the wing.
        span (float): Span of the wing.
        N_elements (int): Number of elements in the span direction.
        nelem_span (int): Number of elements in the span direction.
        airfoil_profile (str): Airfoil profile to be used for the wing sections, can be one of the NACA 4 digit airfoils, e.g. "NACA0012" or "NACA4412".
        airfoil_table (str): Path to the airfoil table file.
        end_chord (float): Chord length at the wing tip.

    Returns:
        None: Creates or updates the ParamWing.in file in the specified folder with the wing definition if the content is different.
    """

    file_path = f"{folder_path}/ParamWing.in"

    # Calculate the center chord of the elliptic wing
    A = span**2 / AR
    center_chord = height_of_an_ellipse(A, span / 2)

    # Calculate the chord length sections for the elliptic wing
    ll_chord_sections = []
    for n in range(0, int(N_elements / 2)):
        x = span / N_elements * n
        y = center_chord / 2 * np.sqrt(1 - x**2 / (span / 2)**2)
        ll_chord_sections.append(np.round(2 * y, 5))

    # Generate the new content for the file
    first_block = f"""mesh_file_type = parametric
el_type = l

mesh_symmetry = T
symmetry_point = (/0.0 ,0.0, 0.0/)
symmetry_normal = (/0.0 , 1.0, 0.0/)

starting_point = (/0.0,0.0,0.0/)
! reference_chord_fraction = 0.5

type_chord = uniform
"""

    sections_and_regions = ""
    for i, y in enumerate(ll_chord_sections, start=1):
        sections_and_regions += f"""
! section {i}
chord = {y}
twist = 0.0 ! deg
airfoil_table = {airfoil_table}
airfoil = {airfoil_profile}

! region {i}
span = {np.round(span / N_elements, 5)}
sweep = 0.0 ! deg
dihed = 0.0 ! deg
nelem_span = {nelem_span}
type_span = uniform
"""

    sections_and_regions += f"""
! section {N_elements / 2 + 1}
chord = {end_chord}
twist = 0.0 ! deg
airfoil_table = {airfoil_table}
airfoil = {airfoil_profile}
"""

    new_content = first_block + sections_and_regions

    # Check if the file exists and compare the content
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            existing_content = file.read()

        # Update the file only if the content is different
        if existing_content != new_content:
            with open(file_path, 'w') as file:
                file.write(new_content)
    else:
        # Create the file and write the new content
        with open(file_path, 'w') as file:
            file.write(new_content)
