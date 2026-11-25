#!/usr/bin/python3

from ctypes import WinDLL
from pathlib import Path,WindowsPath
from typing import Mapping,Optional,Union
from sys import argv as sys_argv

from yaml import (load as yaml_load, Loader as yaml_Loader)

from WUEFI_ctypes import import_GetFwType
from WPrivilege import query_proc_priv_info,env_gain_extra_priv
from WUtils_windows import get_fwtype

from WDisks import (
	init_kernel32 as WDisks_Client,
	# from_mountpoint_get_volume_ex,
	mount_volume,
	# mount_esp_partition,
	get_free_mountpoint,
	get_winvol_boot,
	get_winvol_system
)
from depmgmt import process_rscl
from utils import get_path_from_str,get_total_size

_FWTYPE_LEGACY=1
_FWTYPE_UEFI=2

_KN_LEGACY="legacy"
_KN_UEFI="uefi"
_KN_FILES="files"
_KN_GRUB4DOS="config.grub4dos"
_KN_GRUB2="config.grub2"
_KN_SYSTEMDBOOT="config.systemd-boot"
_KN_BOOTPART="content.boot"
_KN_SYSPART="content.system"

def util_from_yaml_read_str(value:Optional[str])->Optional[str]:

	if not isinstance(value,str):
		return None

	value_ok=value.strip()

	if not len(value_ok.splitlines())==1:
		return None

	return value_ok

def step_read_config(
		basedir:Path,
		fwtype:int,
		test_only:bool=False
	)->Union[bool,Mapping]:

	stem="install"

	path_config=basedir.joinpath(f"{stem}.yml")
	if not path_config.is_file():
		path_config=basedir.joinpath(f"{stem}.yaml")
	if not path_config.is_file():
		raise FileNotFoundError(f"{stem}.yaml (or yml) manifest not found")

	data=yaml_load(
		path_config.read_text(),
		Loader=yaml_Loader
	)

	print("FROM YAML:",data)

	err_found=False
	err_msg:Optional[str]=None

	# VERSION 1

	config_ready={}

	if fwtype==_FWTYPE_LEGACY:

		k=_KN_LEGACY
		if k in data.keys():
			if not isinstance(data[k],Mapping):
				return {"error":f"expected '{k}' to be a map"}

			kk=_KN_GRUB4DOS
			if kk in data[k].keys():
				v=util_from_yaml_read_str(data[k][kk])
				if v is None:
					return {"error":f"expected '{k}/{kk}' to be a string"}

				config_ready.update({kk:v})

			kk=_KN_FILES
			if kk in data[k].keys():
				if not isinstance(data[k][kk],Mapping):
					return {"error":f"expected '{k}/{kk}' to be a map"}

				for kkk in (_KN_BOOTPART,_KN_SYSPART):

					if kkk not in data[k][kk].keys():
						continue

					if not isinstance(data[k][kk][kkk],list):
						err_found=True
						err_msg=f"expected '{k}/{kk}/{kkk}' to be a list"
						break

					config_ready.update({kkk:data[k][kk][kkk]})

	if fwtype==_FWTYPE_UEFI:

		k=_KN_UEFI
		if k in data.keys():
			if not isinstance(data[k],Mapping):
				return {"error":f"expected '{k}' to be a map"}

			kk=_KN_GRUB2
			if kk in data[k].keys():
				v=util_from_yaml_read_str(data[k][kk])
				if v is None:
					return {"error":f"expected '{k}/{kk}' to be a string"}

				config_ready.update({kk:v})

			kk=_KN_SYSTEMDBOOT
			if kk in data[k].keys():
				v=util_from_yaml_read_str(data[k][kk])
				if v is None:
					return {"error":f"expected '{k}/{kk}' to be a string"}

				config_ready.update({kk:v})

			kk=_KN_FILES
			if kk in data[k].keys():
				if not isinstance(data[k][kk],Mapping):
					return {"error":f"expected '{k}/{kk}' to be a map"}

				for kkk in (_KN_BOOTPART,_KN_SYSPART):

					if kkk not in data[k][kk].keys():
						continue

					if not isinstance(data[k][kk][kkk],list):
						err_found=True
						err_msg=f"expected '{k}/{kk}/{kkk}' to be a list"
						break

					config_ready.update({kkk:data[k][kk][kkk]})

	if not err_found:

		k=_KN_FILES
		if k in data.keys():

			if not isinstance(data[k],Mapping):
				return {"error":f"expected '{k}' to be a map"}

			for kk in (_KN_BOOTPART,_KN_SYSPART):

				if kk not in data[k].keys():
					continue

				if not isinstance(data[k][kk],list):
					err_found=True
					err_msg=f"expected '{k}/{kk}' to be a list"
					break

				config_ready.update({f"{k}/{kk}":data[k][kk]})

	if err_found:
		return {"error":err_msg}

	return config_ready

def step_from_config_get_files(
		basedir:Path,
		config:Mapping
	)->Mapping:

	result={}

	for k in (

			# General files
				f"{_KN_FILES}/{_KN_BOOTPART}",
				f"{_KN_FILES}/{_KN_SYSPART}",

			# Legacy boot specific files
				f"{_KN_LEGACY}/{_KN_FILES}/{_KN_BOOTPART}",
				f"{_KN_LEGACY}/{_KN_FILES}/{_KN_SYSPART}",

			# UEFI Boot specific files
				f"{_KN_UEFI}/{_KN_FILES}/{_KN_BOOTPART}",
				f"{_KN_UEFI}/{_KN_FILES}/{_KN_SYSPART}",
		):

		if k not in config.keys():
			continue

		if not isinstance(config[k],list):
			break

		result.update({k:process_rscl(config[k])})

		if len(result[k])==0:
			return {"error":f"value in {k}"}
			break

	return result

def step_from_config_get_availops(
		basedir:Path,
		fwtype:int,
		config:Mapping
	)->Mapping:

	# Get the available options from the config as well as verify the existante
	# of the file paths provided by the vendor/guest

	availops=[]

	if fwtype==_FWTYPE_LEGACY:

		found=0

		for k in [_KN_GRUB4DOS]:

			ok=(k in config.keys())

			if not ok:

				continue

			if ok:

				if not isinstance(config[k],str):
					return {"error":f"declared {k} is not a string"}

				if not get_path_from_str(config[k].strip(),basedir,verify_existance=True):
					return {"error":f"declared {k} not found"}

			found=found+1
			availops.append(k)

		if found==0:
			return {
				"error":f"config for grub4dos ({_KN_GRUB4DOS}) is missing"
			}


	if fwtype==_FWTYPE_UEFI:

		found=0

		for k in [_KN_GRUB2,_KN_SYSTEMDBOOT]:

			ok=(k in config.keys())

			if not ok:

				continue

			if ok:

				if not isinstance(config[k],str):
					return {"error":f"declared {k} is not a string"}

				if not get_path_from_str(
						config[k].strip(),
						anchor=basedir,
						verify_existance=True
					):
					return {"error":f"declared {k} not found"}

			found=found+1
			availops.append(k)

		if found==0:
			return {
				"error":(
					f"systemd-boot ({_KN_SYSTEMDBOOT}) and "
						f"grub2 ({_KN_GRUB2}) configs are missing"
					)
			}

	return {"availops":availops}

def step_get_disk_and_vols(
		plsize_system:int=0,
		plsize_boot:int=0,
		test_only:bool=False,
	)->Mapping:

	# Returns the disk index, and the volume(s) holding the boot partition and
	# the system partition, and it makes sure that both are mounted

	# NOTE:
	# by providing payload sizes

	k32:WinDLL=WDisks_Client()

	volsystem=get_winvol_system(k32,get_spm=True,get_voldata=True)

	volsystem_extents=volsystem.get("volume_extents",[])
	if not len(volsystem_extents)==2:
		return {"error":"(volsystem) no volume extents found"}

	disk_index1=volsystem_extents[0].get("DiskNumber",-1)
	if disk_index1<0:
		return {"error":"(volsystem) disk index not found"}

	volsystem_paths=volsystem.get("volume_paths",[])
	if len(volsystem_paths)==0:
		return {"error":"(volsystem) volume paths not found"}

	drive_letter1=volsystem_paths[0]

	volboot=get_winvol_boot(k32,get_spm=True,get_voldata=True)

	volboot_extents=volboot.get("volume_extents",[])
	if len(volboot_extents)==0:
		return {"error":"(volboot) no volume extents found"}

	disk_index2=volboot_extents[0].get("DiskNumber",-1)
	if disk_index2<0:
		return {"error":"(volboot) disk index not found"}

	if not disk_index1==disk_index2:
		return {"error":"(volboot) disk indexes do not match"}

	drive_letter2:Optional[str]=None

	volboot_paths=volboot.get("volume_paths",[])

	empty=(len(volboot_paths)==0)

	if not empty:

		drive_letter2=volboot_paths[0]

	if empty:

		volboot_name=volboot.get("volume_name")

		if not test_only:

			letter2=get_free_mountpoint(k32,ret_as_drive=True)

			if not mount_volume(volboot_name,letter2):
				return {"error","Failed to mount the boot partition"}

			drive_letter2=f"{letter2}\\"

	if plsize_boot>0 and plsize_system>0:

		volboot_space=volboot.get("volume_space")
		if not isinstance(volboot_space,tuple):
			return {"error":"(volboot) volume_space missing"}
		if not len(volboot_space)==3:
			return {"error":"(volboot) volume_space in wrong format"}

		volsystem_space=volsystem.get("volume_space")
		if not isinstance(volsystem_space,tuple):
			return {"error":"(volsystem) volume_space missing"}
		if not len(volsystem_space)==3:
			return {"error":"(volsystem) volume_space in wrong format"}

		unified=(drive_letter1 == drive_letter2)

		if unified:

			# Require 2 GB of extra space

			ns=1024*1024*1024*2
			space_required=ns+plsize_boot+plsize_system
			space_free=volboot_space[2]+volsystem_space[2]
			if space_required>space_free:
				return {"error":"not enought free space"}

		if not unified:

			ns=1024*1024*8
			space_required=ns+plsize_boot
			space_free=volboot_space[2]
			if space_required>space_free:
				return {"error":"not enought free space"}

			ns=1024*1024*1024*2
			space_required=ns+plsize_system
			space_free=volsystem_space[2]
			if space_required>space_free:
				return {"error":"not enought free space"}

	return {
		"disk_index":disk_index1,
		"drive_system":drive_letter1,
		"drive_boot":drive_letter2
	}

def main(basedir:Path,test:bool=False):

	if not query_proc_priv_info():
		print("Run as administrator")
		return None

	env_gain_extra_priv()


	print("\nDATA_FWTYPE:")
	data_fwtype=get_fwtype(import_GetFwType())
	if data_fwtype not in (_FWTYPE_LEGACY,_FWTYPE_UEFI):
		print(
			"Cannot determine wether the "
				"system is UEFI or BIOS/LEGACY"
		)
		return None
	print(data_fwtype)

	print("\nDATA_CONFIG:")
	data_config=step_read_config(basedir,fwtype=data_fwtype)
	print(data_config)

	print("\nDATA_AVAILOPS:")
	data_availops=step_from_config_get_availops(basedir,data_fwtype,data_config)
	print(data_availops)

	print("\nDATA_FS:")
	data_fs=step_get_disk_and_vols(plsize_boot=0,plsize_system=0,test_only=test)
	print(data_fs)

	req_size_boot=0
	req_size_system=0

	print("\nRSCL")
	data_rscl=step_from_config_get_files(basedir,config)
	print(data_rscl)

if __name__=="__main__":

	basedir=Path(sys_argv[0]).parent

	main(basedir,True)
