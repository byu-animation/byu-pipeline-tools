if ( "$arg1" != "" ) then
    opproperty -f -F Properties $arg1 prman21.0 default_output
    opparm $arg1 target ( "prman21.0" )
    opparm $arg1 soho_pipecmd ( "prman" )
    opparm $arg1 ri_visibletransmission ( 1 ) ri_visiblespecular ( 1 )
    opparm $arg1 ri_pixelsamples ( 3 3 )
endif
