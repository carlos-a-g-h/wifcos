#!/usr/bin/python3


from ctypes import WinDLL

from pathlib import Path,WindowsPath
from typing import Mapping,Optional,Union

from depmgmt import (
	get_fpath_systemdboot,
	get_fpath_systemdboot_signed
)

def write_loader_conf_with_single_entry(
		root:str,fpath_entry:Path,
		timeout:int=10,
	)->bool:

	fpath_loader_conf=Path(
		root,
		"loader",
		"loader.conf"
	)

	fpath_entry_ok=Path(
		root,
		"loader",
		"entries",
		fpath_entry.name
	)

	content=(
		f"default {fpath_entry.name}\n"
		f"timeout {timeout}\n"
		"auto-firmware yes\n"
		"auto-entries yes"
		"console-mode auto"
		"editor no"
	)

	try:

		fpath_loader_conf.parent.mkdir(exist_ok=True,parents=True)
		fpath_loader_conf.write_text(content)

		content=fpath_entry.read_text()
		fpath_entry_ok.parent.mkdir(exist_ok=True,parents=True)
		fpath_entry_ok.write_text(content)

	except Exception as exc:
		print(exc)
		return False

	return True
