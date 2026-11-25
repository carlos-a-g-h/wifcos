#!/usr/bin/python3

from pathlib import Path
from typing import Optional,Union

from utils import get_path_from_str

def get_fpath(
		basedir:Path,
		pathlst:list,
		check_only:bool=False
	)->Union[bool,Optional[Path]]:

	pl=basedir.joinpath(*pathlst)

	if not pl.is_file():
		return None

	print(pl)

	return pl.absolute()

def get_fpath_grldr(
		basedir:Path,
		check_only:bool=False
	)->Union[bool,Optional[Path]]:

	return get_fpath(
		basedir,
		[
			"dependency.grub4dos",
			"grub4dos",
			"grldr"
		],
		check_only=check_only
	)

def get_fpath_grldr_mbr(
		basedir:Path,
		check_only:bool=False
	)->Union[bool,Optional[Path]]:

	return get_fpath(
		basedir,
		[
			"dependency.grub4dos",
			"grub4dos",
			"grldr.mbr"
		],
		check_only=check_only
	)

def get_fpath_grubinst_exe(
		basedir:Path,
		check_only:bool=False
	)->Union[bool,Optional[Path]]:

	return get_fpath(
		basedir,
		[
			"dependency.grubinst",
			"grubinst",
			"grubinst.exe"
		],
		check_only=check_only
	)


def get_fpath_grub2_efi(
		basedir:Path,
		check_only:bool=False
	)->Union[bool,Optional[Path]]:

	return get_fpath(
		basedir,
		[
			"dependency.grub2-efi",
			"grub2.x86_64.efi"
		],
		check_only=check_only
	)

def get_fpath_systemdboot(
		basedir:Path,
		check_only:bool=False
	)->Union[bool,Optional[Path]]:

	return get_fpath(
		basedir,
		[
			"dependency.systemd-boot",
			"systemd-boot",
			"systemd-bootx64.efi"
		],
		check_only=check_only
	)

def get_fpath_systemdboot_signed(
		basedir:Path,
		check_only:bool=False
	)->Union[bool,Optional[Path]]:

	return get_fpath(
		basedir,
		[
			"dependency.systemd-boot",
			"systemd-boot",
			"systemd-bootx64.efi.signed"
		],
		check_only=check_only
	)

def util_path_abs_to_rel(
		bdir:Optional[Path],pl:Path,
		must_exist:bool=False
	)->Optional[Path]:

	plr=None
	ok=pl.is_absolute()
	if ok:
		plr=pl.relative_to(pl.parts[0])

	if not ok:
		plr=pl

	if bdir is None:
		return plr

	plr_ok=bdir.joinpath(plr)
	plr_ok_ok=plr_ok.resolve()
	if must_exist:
		if not plr_ok_ok.exists():
			return None

	return plr_ok_ok

def from_line_get_resource(
		basedir:Path,
		line:str,
		test:bool=False,
		dest_only:bool=False
	)->Union[bool,Optional[Path],Optional[tuple[Path,Path]]]:

	line_ok=line.strip()

	spec_dest=(":" in line_ok)

	if not spec_dest:

		if dest_only:
			return get_path_from_str(
				spec_dest,
				anchor=basedir
			)

		if test:
			return get_path_from_str(
				spec_dest,
				anchor=basedir,
				must_exist=True,
				verify_existance=True
			)

		return get_path_from_str(
			spec_dest,
			anchor=basedir,
			must_exist=True
		)

	# Specified destination

	parts=line_ok.split(sep=":")
	if not len(parts)==2:
		# print(2)
		return None

	orig_str:Optional[str]=None
	orig_ok:Optional[Path]=None

	if not dest_only:

		orig_str=parts[0].strip()
		if len(orig_str)==0:
			if test:
				return False
			return None

	dest_str=parts[0].strip()
	if len(dest_str)==0:
		if test:
			return False
		return None

	if not dest_only:

		orig_ok=get_path_from_str(
			parts[0].strip(),
			anchor=basedir,
			must_exist=True,
		)
		if orig_ok is None:
			if test:
				return False
			return None

	dest_ok=get_path_from_str(
		parts[1].str(),
		anchor=basedir
	)
	if dest_ok is None:
		if test:
			return False
		return None

	# DEST

	if dest_only:

		return dest_ok

	# ( ORIG , DEST )

	if test:
		return True
	return (orig_ok,dest_ok)

def process_rscl(
		basedir:Path,
		rsclist:list,
		test:bool=False
	)->list:

	# From resource list get resources

	resources=[]
	fatal=False

	for line in rsclist:

		resources.append(
			from_line_get_resource(
				basedir,line,
				test=test
			)
		)

		if resources[-1] is None:
			fatal=True
			break

	if fatal:
		return []

	return resources
