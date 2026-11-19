#!/usr/bin/python3

from pathlib import Path,WindowsPath
from typing import Mapping,Optional,Union

from WDisks import from_mountpoint_get_volume_ex
from WUtils_windows import wsubproc,copy_files

_MENU_LST_FILENAME="menu.lst"

_MENU_LST_CONTENTS="""
timeout 10

title Quit
quit

title Reboot
reboot

title Shutdown
halt
"""

def get_path_grldr(
		basedir:Path,
		check_only:bool=False
	)->Optional[Path]:

	pl=basedir.joinpath(
		"dependency.grub4dos",
		"grub4dos",
		"grldr"
	)
	if not pl.is_file():
		return None

	print("GRLDR:",pl)

	return pl.absolute()

def get_path_grldr_mbr(
		basedir:Path,
		check_only:bool=False
	)->Optional[Path]:

	pl=basedir.joinpath(
		"dependency.grub4dos",
		"grub4dos",
		"grldr.mbr"
	)
	if not pl.is_file():
		return None

	print("GRLDR.MBR:",pl)

	return pl.absolute()

def get_path_grubinst_exe(basedir:Path)->Optional[Path]:

	pl=basedir.joinpath(
		"dependency.grubinst",
		"grubinst",
		"grubinst.exe"
	)
	if not pl.is_file():
		return None

	print("GRUBINST.EXE:",pl)

	return pl.absolute()

def copy_menu_lst(
		fpath:Optional[Path],
		dpath:Path,
		debug:bool=False
	)->bool:

	dpath_ok=dpath.joinpath(_MENU_LST_FILENAME)

	if fpath is None:

		try:
			dpath_ok.write_text(_MENU_LST_CONTENTS)
		except Exception as exc:
			print("FATAL:",exc)
			return False

		return True

	if fpath.is_file():

		# if debug:
		# 	print("Copying provided MENU.LST...")

		return copy_files(fpath,dpath_ok)

	if fpath.is_dir():

		# if debug:
		# 	print("FInding a MENU.LST in the provided directory...")

		fpath_ok=fpath.joinpath(_MENU_LST_FILENAME)

		if fpath_ok.is_file():

			return copy_files(fpath_ok,dpath_ok)

		if not fpath_ok.is_file():

			try:
				dpath_ok.write_text(_MENU_LST_CONTENTS)
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
	fpath_grubinst_exe=get_path_grubinst_exe(basedir)
	if fpath_grubinst_exe is None:
		return (step,"GRUBINST.EXE not found",{})

	step=step+1
	fpath_grldr=get_path_grldr(basedir)
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
	fpath_grldr=get_path_grldr(basedir)
	if fpath_grldr is None:
		return (step,"GRLDR not found",{})

	step=step+1
	fpath_grldr_mbr=get_path_grldr_mbr(basedir)
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
