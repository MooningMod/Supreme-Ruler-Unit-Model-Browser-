# Supreme Ruler Unit Model Browser

https://www.youtube.com/watch?v=QW5LWEKzHeY

Unit Model Browser r04
Hey everyone! New update for the Unit Model Browser:
Sorting: You can now sort the unit list by ID (ascending/descending), Name (A-Z / Z-A), Class, or Picnum
This was requested - now you can easily browse units by number range to find specific classes

Region Filtering
Added full region code support based on the official wiki
SR2030: supports both UPPERCASE and lowercase codes (e.g., U for USA, b for Brazil, h for Poland)
SRU: uppercase only with grouped regions (e.g., R = Russia/Ukraine/Soviet/Belarus)
Dropdown updates automatically when switching between games
Custom option if you need to filter by specific codes

Mirrored Models Fix
If your models appear mirrored in the DirectXTK viewer, I've included a C++ patch that adds a Z key toggle to switch between left-handed and right-handed coordinate systems
Just press Z and the model reloads with correct orientation
Let me know if you find any issues

1. Installation

Download and extract the ZIP archive.

Make sure the folder contains the following files:

UnitModelBrowser.exe
DirectXTKModelViewer.exe
LICENSE_DirectXTK.txt
config.json
mview.exe   (you must provide this yourself; see below)


The tool is completely portable and requires no installation.

2. External 3D Viewers Supported

The Unit Model Browser uses external applications to display 3D models. Two viewers are supported.

A. DirectXTK Model Viewer (Redistributable)

This viewer is included in the package because it is released under the MIT license and can be redistributed.

Official GitHub repository:

https://github.com/walbourn/directxtkmodelviewer

The included executable was compiled by me and includes the following patch:

DirectXTKModelViewer_cmdline.patch

This patch adds command-line support, allowing the browser to run:

DirectXTKModelViewer.exe <mesh_path>

so that the viewer automatically opens the selected model without user interaction.

B. mview.exe (Not Redistributable)

The classic mesh viewer used for .x models, known as mview.exe, is distributed By Microsoft. Therefore the program cannot include it in this package. Just copy mview.exe into the same folder as UnitModelBrowser.exe

This step is required if you want to use mview.exe as viewer for SRU.

3. Configuring the Program

Inside the application, open the Settings tab.

For each profile (SR2030 and SRU), configure:

Unit File (default.unit)

Meshes Folder (Graphics/Meshes)

Viewer Executable (choose either DirectXTKModelViewer.exe or mview.exe)

You may switch between SR2030 and SRU at any time.

Configuration is saved automatically into:

config.json

4. How to Use the Browser

Launch UnitModelBrowser.exe.

Select the desired profile (SR2030 or SRU).

Load unit data using the configured .unit file.

Browse or search units by name, ID, category, or picnum.

View mesh status, file names, and associated textures.

Double-click a unit or use the "Launch 3D Viewer" button to open a viewer instance.

You may open multiple viewer windows for side-by-side comparison.

5. Notes for Modders

The tool is designed to simplify model analysis, especially when preparing mods. It is fully external and has no impact on the game installation.

6. Legal Notes

DirectXTKModelViewer.exe is distributed under the MIT License. 
The viewer is compiled from the open-source DirectXTK Model Viewer project:
https://github.com/walbourn/directxtkmodelviewer
A small patch (DirectXTKModelViewer_cmdline.patch) was applied to enable command-line loading of mesh files. The original MIT license is included as LICENSE DirectXTKModelViewer_Desktop

Supreme Ruler is a trademark of Battlegoat Studios. This tool is an independent community utility



