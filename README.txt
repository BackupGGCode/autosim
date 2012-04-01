PREREQUISITES:

PhysX_2.8.4.6_for_PC_Core.msi Available at: developer.nvidia.com (requires a user account)
pygame-1.9.1.win32-py2.7.msi Available at: http://www.pygame.org/download.shtml

If using a Logitech G25 steering wheel:
Logitech Gaming Software for Multilingual 64-bit Windows 7. Available at: http://www.logitech.com/en-us/441/131?section=downloads&bit=&osid=14

INSTALING:

This application requires that Panda3D 1.8.0 is build from source (using MSVC2008) with
the applied patches found in the Panda-src-modifications.
The patches were made to further implement the NxWheelShape functionality in PhysX which
is only partially implemented in Panda3D.

It is probably wise to install the PhysX SDK before building the Panda3D engine.

Copy the following files to the autosim directory:
	cudart32_90_9.dll
	NxCharacter.dll
	PhysXCore.dll
	PhysXDevice.dll
	PhysXLoader.dll


RUNNING:

Run the application with 'python default.py'
To toggle between keyboard control and a steering wheel control (tested with a logitech G25) change lines 52-53
so the inputHandler is of desired type.

LEGAL:

Land Rover Defender car model received from: 	www.dmi-3d.net
Gravel sounds received from:					www.alwaysfree.nl/free_sound_effects/cars/slides/Tires_On_Gravel_Steady.html
Land Rover Defender audio files received from:	www.salamisound.com
Speedometer textures are from:                  www.gtaforums.com/index.php?showtopic=494178
