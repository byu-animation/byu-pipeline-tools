if ( "$arg1" != "" ) then
    opproperty -f -F Properties $arg1 prman21.0 default_output_ris
    opparm $arg1 target ( "prman21.0" )
    opparm $arg1 soho_pipecmd ( "prman" )
    opparm $arg1 soho_rismode ( 1 )

    opparm $arg1 ri_visibletransmission ( 1 )
    opparm $arg1 ri_hider ( "raytrace" )
    opparm $arg1 ri_maxsamples ( 64 )
    opparm $arg1 ri_incremental ( 1 )

    opproperty -f -F Render $arg1 prman21.0 ri_diffusedepth
    opproperty -f -F Render $arg1 prman21.0 ri_speculardepth
    opparm $arg1 ri_diffusedepth ( 7 )
    opparm $arg1 ri_speculardepth ( 3 )

    opparm $arg1 ri_device "it"

    opparm $arg1 tprerender ( 1 )
    opparm $arg1 prerender "import ris_render_scripts;ris_render_scripts.pre_render()"
    opparm $arg1 lprerender "python"

    opparm $arg1 tpreframe ( 1 )
    opparm $arg1 preframe "import ris_render_scripts;ris_render_scripts.pre_frame()"
    opparm $arg1 lpreframe "python"

    opparm $arg1 tpostframe ( 1 )
    opparm $arg1 postframe "import ris_render_scripts;ris_render_scripts.post_frame()"
    opparm $arg1 lpostframe "python"

    opparm $arg1 tpostrender ( 1 )
    opparm $arg1 postrender "import ris_render_scripts;ris_render_scripts.post_render()"
    opparm $arg1 lpostrender "python"

    opspare -a -t toggle -s 1 -l "Expand Rib Archives" -v 1 expand_rib_archives $arg1

    set location = `run("oppwf")`
    opcf /out
    set shopnet = `run("opadd -v shopnet")`
    opcf $shopnet
    set risnet = `run("opadd -v risnet")`
    opcf $risnet
    set integrator = `run("opadd -v pxrvcm")`

    opcf $location
    opparm $arg1 shop_integratorpath `run("echo /out/$shopnet/$risnet/$integrator")`
    opparm $arg1 camera "/obj/byu_camera1/_/_/cam"

endif
