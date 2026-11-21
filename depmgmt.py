#!/usr/bin/python3

from pathlib import Path
from typing import Optional,Union

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

		if line_ok.startswith("/"):
			line_ok=f".{line_ok}"

		pl=util_path_abs_to_rel(
			basedir,
			Path(line_ok.strip()),
			must_exist=True
		)
		print("PL:",pl)
		if pl is None:
			return None

		dest=pl.relative_to(basedir)
		if dest_only:
			return dest

		return (pl,dest)

	parts=line_ok.split(sep=":")
	if not len(parts)==2:
		# print(2)
		return None

	pl_str=parts[0].strip()
	dest_str=parts[1].strip()

	if len(pl_str)==0:
		return None

	if len(dest_str)==0:
		return None

	if pl_str.startswith("/"):
		pl_str=f".{pl_str}"

	if dest_str.startswith("/"):
		dest_str=f".{dest_str}"

	dest=util_path_abs_to_rel(
		None,
		Path(dest_str.strip())
	)
	if dest_only:
		# print(3)
		return dest

	pl=util_path_abs_to_rel(
		basedir,
		Path(pl_str.strip()),
		must_exist=True
	)
	if pl is None:
		# print(4)
		return None

	return (pl,dest)
