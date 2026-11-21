#!/usr/bin/python3

from ctypes import WinDLL

from pathlib import Path,WindowsPath
from typing import Mapping,Optional,Union

from WDisks import (
	init_kernel32 as WDisks_Client,
	from_mountpoint_get_volume_ex,
	mount_volume,
	get_free_mountpoint,
	get_winvol_boot,
	get_winvol_system
)
from WUtils_windows import wsubproc,copy_files

from depmgmt import (
	get_fpath_grldr,
	get_fpath_grldr_mbr,
	get_fpath_grubinst_exe
)

_MENU_LST_FILENAME="menu.lst"

_MENU_LST_CONTENT_BOOTMGR="""
Windows
chainloader /bootmgr
"""

_MENU_LST_CONTENT_OPTS="""
title Reboot
reboot

title Shutdown
halt
"""
def copy_menu_lst(
		fpath:Optional[Path],
		dpath:Path,
		local:bool=False,
		debug:bool=False,
	)->bool:

	dpath_ok=dpath.joinpath(_MENU_LST_FILENAME)

	if fpath is None:

		try:
			dpath_ok.write_text(
				"timeout 10\n"
				f"{_MENU_LST_CONTENT_BOOTMGR}\n"
				f"{_MENU_LST_CONTENT_OPTS}"
			)
		except Exception as exc:
			print("FATAL:",exc)
			return False

		return True

	if fpath.is_file():

		return copy_files(fpath,dpath_ok)

	if fpath.is_dir():

		fpath_ok=fpath.joinpath(_MENU_LST_FILENAME)

		if fpath_ok.is_file():

			return copy_files(fpath_ok,dpath_ok)

		if not fpath_ok.is_file():

			try:
				dpath_ok.write_text(
					"timeout 10\n"
					f"{_MENU_LST_CONTENT_BOOTMGR}\n"
					f"{_MENU_LST_CONTENT_OPTS}"
				)
			except Exception as exc:
				print("FATAL:",exc)
				return False

			return True

	return False

def main_grubinst(
		basedir:Path,
		drive_letter:str,
		disk_index:int=-1,
		fpath_menu_lst:Union[Path,WindowsPath]=None,
		test_only:bool=False,
		debug:bool=False
	)->tuple[int,Optional[str],Mapping]:

	# Installs Grub4DOS to a disk using grubinst

	step=0

	##############################################################################

	step=step+1
	fpath_grubinst_exe=get_fpath_grubinst_exe(basedir)
	if fpath_grubinst_exe is None:
		return (step,"GRUBINST.EXE not found",{})

	step=step+1
	fpath_grldr=get_fpath_grldr(basedir)
	if fpath_grldr is None:
		return (step,"GRLDR not found",{})

	disk_index_ok=disk_index

	if disk_index_ok<0 or test_only:

		volume=from_mountpoint_get_volume_ex(
			drive_letter,
			get_spm=True,
			debug=debug
		)

		step=step+1
		volume_paths=volume.get("volume_paths",[])
		if len(volume_paths)==0:
			return (step,"Volume Paths not found...?",volume)

		step=step+1
		if drive_letter not in volume_paths:
			return (step,"The given path is not among the volume paths",volume)

		step=step+1
		volume_extents=volume.get("volume_extents",[])
		if not len(volume_extents)==2:
			return (step,"Volume Extents not found...?",volume)

		step=step+1
		if not isinstance(volume_extents[0],Mapping):
			return (step,"Volume Extents not found",volume)

		step=step+1
		tmp=volume_extents[0].get("DiskNumber",-1)
		if tmp<0:
			return (step,"DiskNumber not found within the Volume Extents",volume)

		step=step+1

		if not test_only:
			disk_index_ok=tmp

		if test_only:
			if not disk_index<0:
				if not tmp==disk_index_ok:
					return (
						step,
						"the DiskNumber does not match the Disk index that was "
							"given as an argument",
						volume
					)

			disk_index_ok=tmp

		step=step+1
		if not isinstance(volume_extents[-1],Mapping):
			return (
				step,"The last object in the Volume Extents is not a Mapping",volume)

		step=step+1
		if not volume_extents[-1].get("part_style_name")=="MBR":
			return (step,"The partition layout is not valid",volume)


	hard_disk=f"(hd{disk_index_ok})"

	command=[str(fpath_grubinst_exe)]
	if test_only:
		command.append("--read-only")

	command.extend([
		"--verbose",
		"--time-out=0",
		hard_disk
	])

	# NOTE:
	# Apparently, wether grubinst is successful or not, the output is on the
	# STDERR instead of the STDOUT

	step=step+1
	result=wsubproc(command,verbose=True)
	if not result[0]==0:
		return (step,result[2].strip(),{})

	# COPY FILES (?)

	step=step+1
	if not copy_menu_lst(
			fpath_menu_lst,
			Path(drive_letter)
		):
		return (step,"Failed to copy MENU.LST",{})

	step=step+1
	if not copy_files(
			fpath_grldr,
			Path(drive_letter,"grldr")
		):
		return (step,"Failed to copy GRLDR",{})

	return (0,None,{})

# def step_get_disk_and_vols(
# 		plsize_system:int=-1,
# 		plsize_boot:int=-1,
# 		test_only:bool=False
# 	)->Mapping:

# 	# ONLY FOR DUAL BOOT SETUPS

# 	# Returns the disk index, and the volume(s) holding the boot partition and
# 	# the system partition, and it makes sure that both are mounted

# 	# NOTE:
# 	# by providing payload sizes

# 	k32:WinDLL=WDisks_Client()

# 	volsystem=get_winvol_system(k32,get_spm=True,get_voldata=True)

# 	volsystem_extents=volsystem.get("volume_extents",[])
# 	if len(volsystem_extents)==0:
# 		return {"error":"(volsystem) no volume extents found"}

# 	disk_index1=volsystem_extents[0].get("DiskNumber",-1)
# 	if disk_index1<0:
# 		return {"error":"(volsystem) disk index not found"}

# 	# Since this is teh system drive, it should have ONE volume path

# 	volsystem_paths=volsystem.get("volume_paths",[])
# 	if len(volsystem_paths)==0:
# 		return {"error":"(volsystem) volume paths not found"}

# 	drive_letter1=volsystem_paths[0]

# 	volboot=get_winvol_boot(k32,get_spm=True,get_voldata=True)

# 	volboot_extents=volboot.get("volume_extents",[])
# 	if len(volboot_extents)==0:
# 		return {"error":"(volboot) no volume extents found"}

# 	disk_index2=volboot_extents[0].get("DiskNumber",-1)
# 	if disk_index2<0:
# 		return {"error":"(volboot) disk index not found"}

# 	if not disk_index1==disk_index2:
# 		return {"error":"(volboot) disk indexes do not match"}

# 	drive_letter2:Optional[str]=None

# 	volboot_paths=volboot.get("volume_paths",[])

# 	empty=(len(volboot_paths)==0)

# 	if not empty:

# 		drive_letter2=volboot_paths[0]

# 	if empty:

# 		volboot_name=volboot.get("volume_name")

# 		if not test_only:

# 			drive_letter2=get_free_mountpoint(k32,ret_as_drive=True)

# 			if not mount_volume(volboot_name,drive_letter2):
# 				return {"error","Failed to mount the boot partition"}

# 	if drive_letter1 == drive_letter2:

# 		pass

# 	return {
# 		"drive_system":drive_letter1,
# 		"drive_boot":drive_letter2
# 	}

def main_bcd_system(
		basedir:Path,
		drive_letter:str,
		fpath_menu_lst:Union[Path,WindowsPath]=None,
		test_only:bool=False,
		debug:bool=False
	)->tuple[int,Optional[str],Mapping]:

	# Install Grub4DOS to a local disk by loading it from the system's BCD

	step=0

	step=step+1
	fpath_grldr=get_fpath_grldr(basedir)
	if fpath_grldr is None:
		return (step,"GRLDR not found",{})

	step=step+1
	fpath_grldr_mbr=get_fpath_grldr_mbr(basedir)
	if fpath_grldr_mbr is None:
		return (step,"GRLDR.MBR not found",{})

	# TODO:
	# must detect the boot partition specifically in order to copy the files





if __name__=="__main__":

	from sys import argv as sys_argv

	letter="Y:\\"

	basedir=Path(sys_argv[0]).parent

	result=main_grubinst(basedir,letter)
	if not result[0]==0:
		print("Payload:",result[2])
		raise Exception(result[1])

	print("\nresult:",result)
