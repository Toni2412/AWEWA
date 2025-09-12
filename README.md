# AWEWA
### Airborne Wind Energy Wake Analysis

## Summary

This pipeline lets you **cross-check** your results from [awebox](https://github.com/awebox/awebox) using the open-source mid-fidelity aerodynamic solver [DUST](https://www.dust.polimi.it/).  
You first optimize your trajectory in *awebox*, and this code then helps you translate your trajectory, orientation, and related data into DUST input files.  
The results from DUST can be visualized with tools such as [ParaView](https://www.paraview.org/download/), or directly with this code to produce visualizations like the heatmap shown below:


![Wake evolution](assets/wake_evolution.gif)

## Installing DUST

[DUST](https://www.dust.polimi.it/) is an open-source mid-fidelity aerodynamic solver that was co-developed by **A³ by Airbus** and the Department of Aerospace Science and Technology at Politecnico di Milano.  

There will soon be (or already is) a commercial version of DUST, but there is also an open-source version available.  

Here is my personal guide on how to download DUST, including some of the errors I ran into and how to avoid/fix them:

1. Go to the [official DUST GitHub repository](https://public.gitlab.polimi.it/DAER/dust).
2. Scroll down and click on *installation guidelines*.
3. You will now automatically be on the *master* branch, but to ensure that you are installing the latest version of DUST, switch to the *develop* branch.
4. Choose your operating system and follow the steps (for me, it was Apple Silicon).
5. In my case (Apple Silicon), I ran into the following problems:
   - Several typos in the commands, for example, a double `install` in the first line.  
   - If you use Anaconda, make sure to **deactivate it** before running the commands in the terminal. There seems to be a conflict between Anaconda and CMake.  
   - If the line  
     ```
     brew install cmake lapack blas openblas cgns hdf5 llvm
     ```  
     gives you an error, try removing `blas`. It seems to already be included in `openblas`.
6. Once DUST is installed, I recommend going through the examples by following the *dust quick start* document. Both of these should already be downloaded when you follow the instructions from the [official DUST GitHub repository](https://public.gitlab.polimi.it/DAER/dust).
7. If you run into problems while using DUST, there is a [forum](https://public.gitlab.polimi.it/DAER/dust/-/issues) where you can ask questions or check if someone else has already solved your problem.

---

## Visualisations in ParaView

To visualize the wake, I used [ParaView](https://www.paraview.org/download/). The installation process is very straightforward, and I didn’t run into any issues.  

The DUST examples, as well as the pipeline, will output a folder of `.vtu` files. These contain wake visualizations and can be opened in ParaView.  

- If you open the **entire folder**, you’ll see an animation of how the wake builds up for each time step of your simulation.  
- If you want to examine the wake at a **specific timestep**, open that file directly.
