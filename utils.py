#!/usr/bin/python3

from pathlib import Path
from typing import Optional,Union

# from WUtils_windows import copy_files

def get_total_size(
		items:list,
		debug:bool=False
	)->int:

	# Given a list of files, it returns the size

	# NOTE:
	# If an item is not a file or it does not exist, it immediately fails and
	# returns -1

	size=0

	for p in items:

		if not isinstance(p,Path):
			size=-1
			break

		if not p.is_file():
			size=-1
			break

		size=size+p.stat().st_size

	return size

def get_path_from_str(
		path_str:Path,
		anchor:Optional[Path]=None,
		must_exist:bool=False,
		verify_existance:bool=False
	)->Union[bool,Optional[Path]]:

	# Turns a string into a path

	# NOTE:
	# If the path is absolute, it turns it into a relative path, and if an
	# anchor is provided, the resulting path returned is the anchor combined
	# with the provided path

	path_new:Optional[Path]=None

	path_test=Path(path_str)

	case1=path_test.is_absolute()

	case2=(
		path_str.startswith("/") or
		path_str.startswith("\\")
	)

	is_abs=(case1 or case2)

	if is_abs:

		if case1:
			path_new=Path(*path_test.parts[1:])

		if case2:
			path_str_ok="."+path_str
			path_new=Path(path_str_ok)

	if not is_abs:

		path_new=Path(path_str)

	anchor_it=isinstance(anchor,Path)

	if anchor_it:

		path_w_anchor=anchor.joinpath(path_new).resolve()

		if must_exist:

			ok=path_w_anchor.exists()

			if verify_existance:
				return ok

			if not ok:
				return None

		return path_w_anchor

	# No anchor

	return path_new

def path_scan(
		target_path:Path,
		verify_only:bool=False,
		files_only:bool=False,
	)->Union[bool,Optional[list,Path]]:

	# Reads a path

	if target_path.exists():
		if verify_only:
			return False
		return None

	if target_path.is_file():

		if verify_only:
			return True
		return target_path

	if target_path.is_dir():

		result=[]

		for p in target_path.rglob("*"):
			if p.is_file():
				result.append(p)
			if files_only:
				continue
			if p.is_dir():
				result.append(p)

		if verify_only:
			return True
		return result

	if verify_only:
		return False

	return None

def path_mirror_get(
		path_source:Path,
		path_source_rel:Optional[Path],
		path_dest:Path,
		check_only:bool=False,
		confirm_only:bool=False,
		debug:bool=False
	)->Union[bool,Optional[Path]]:

	is_abs=False
	if path_source.is_absolute():
		is_abs=isinstance(path_source_rel,Path)

	path_ok:Optional[Path]=None

	if debug:
		print("is_abs:",is_abs)

	if is_abs:

		if not path_source.is_relative_to(path_source_rel):

			if check_only or confirm_only:
				if confirm_only:
					return False
				return None

		path_rel=path_source.relative_to(path_source_rel)

		if debug:
			print("path_rel:",path_rel)
			print("path_anchor:",path_dest)
	
		path_ok=path_dest.joinpath(path_rel).resolve()
	
	if not is_abs:

		if debug:
			print("path_rel:",path_source)
			print("path_anchor:",path_dest)
	
		path_ok=path_dest.joinpath(path_source).resolve()

	if check_only or confirm_only:
		ok=path_ok.exists()
		if confirm_only:
			return ok
		if not ok:
			return None

	return path_ok

# if __name__=="__main__":

# 	from sys import argv as sys_argv

# 	basedir=Path(sys_argv[0]).parent.absolute()

# 	example=Path("thing","here")

# 	res1=path_mirror_get(
# 		example,None,basedir,
# 		debug=True,
# 		confirm_only=True
# 	)
# 	print("res1",res1)

# 	ancestor=Path(
# 		basedir.parents[0],
# 		basedir.parents[1],
# 		basedir.parents[2],
# 	)

# 	res2=path_mirror_get(
# 		example.absolute(),ancestor,Path("C:\\","x"),
# 		debug=True,
# 		confirm_only=True
# 	)
# 	print("res2",res2)
