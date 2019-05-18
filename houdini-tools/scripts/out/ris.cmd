# Default script run when a geometry object is created
# $arg1 is the name of the object to create

if ("$HOUDINI_DEFAULT_RIB_RENDERER" == "") then
    set HOUDINI_DEFAULT_RIB_RENDERER = "prman21.0.byu"
endif

set base = "scripts/out/targets/riscreate_$HOUDINI_DEFAULT_RIB_RENDERER.cmd"
set riscreate = `findfile("$base")`
if ( "$riscreate" == "$base") then
    # File wasn't found
    set base = "scripts/out/targets/riscreate_prman21.0.cmd"
    set riscreate = `findfile("$base")`
    if ( "$riscreate" == "$base") then
	set riscreate = ""
    endif
endif

\set noalias = 1
if ( "$arg1" != "" ) then
    if ( "$riscreate" != "" ) then
	source "$riscreate" "$arg1"
    endif
endif
