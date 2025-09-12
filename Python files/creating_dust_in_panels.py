import os



def create_or_change_dust_in_panels(folder_path, t_start, t_end, dt, u_inf, rho_inf):   

    output_path = os.path.join(folder_path, "Output")
    os.makedirs(output_path, exist_ok=True)

    file_path = f"{folder_path}/dust.in"

    n_wake_panels = int(((float(t_end) - float(t_start)) / float(dt)) * 1.2)

    new_content = f"""

    
basename       = ./Output/flapwing

! --- Time parameters ---
tstart = {t_start}
tend = {t_end}
dt = {dt}
dt_out = {dt}
output_start = T
! ndt_update_wake = 1

! --- Restart ---
restart_from_file = F

! --- Geometry files ---
geometry_file = geo_input.h5
reference_file = References.in

! --- stream parameters ---
u_inf = (/ {u_inf}, 0.0, 0.0 /)
rho_inf = {rho_inf}

! wake parameters -------------
n_wake_panels = {n_wake_panels}

! Model parameters -------------------
fmm = F
vortstretch = F
diffusion = F

"""

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