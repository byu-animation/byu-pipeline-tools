# Default script run when a geometry object is created
# $arg1 is the name of the object to create

if ("$HOUDINI_DEFAULT_RIB_RENDERER" == "") then
    set HOUDINI_DEFAULT_RIB_RENDERER = "prman21.0.byu"
endif

set base = "scripts/out/targets/ribcreate_$HOUDINI_DEFAULT_RIB_RENDERER.cmd"
set ribcreate = `findfile("$base")`
if ( "$ribcreate" == "$base") then
    # File wasn't found
    set base = "scripts/out/targets/ribcreate_prman21.0.cmd"
    set ribcreate = `findfile("$base")`
    if ( "$ribcreate" == "$base") then
	set ribcreate = ""
    endif
endif

\set noalias = 1
if ( "$arg1" != "" ) then
    if ( "$ribcreate" != "" ) then
	source "$ribcreate" "$arg1"
    endif
endif
