
def pre_render():
    print("Pre render script executing.")
    #import assemble_v2
    #assemble_v2.rebuildAllAssets()

def pre_frame():
    print ("Pre frame script executing.")

def post_frame():
    print ("Post frame script executing.")

    import hou
    node = hou.pwd()
    rib_outputmode = node.parm("rib_outputmode").evalAsInt()
    expand_rib_archives = node.parm("expand_rib_archives").evalAsInt()

    if rib_outputmode and expand_rib_archives:

        soho_diskfile = node.parm("soho_diskfile").evalAsString()
        rib_expand(soho_diskfile)

def post_render():
    print ("Post render script executing.")

def rib_expand(ribfile):

    from tempfile import mkstemp
    from shutil import move
    from os import fdopen, remove
    import re

    # https://stackoverflow.com/questions/39086/search-and-replace-a-line-in-a-file-in-python
    fh, abs_path = mkstemp()

    with fdopen(fh,'w') as new_file:

        with open(ribfile) as old_file:

            quote_expr = re.compile(r'\"(.+?)\"')
            archive_begin_expr = re.compile(r'ArchiveBegin.*#.*{')
            archive_end_expr = re.compile(r'ArchiveEnd.*#.*}')

            for line in old_file:

                if "ReadArchive" not in line:
                    new_file.write(line)
                    continue

                archive = quote_expr.search(line)
                if not archive:
                    print "Quote_expr: {0}".format(quote_expr)
                    print "Error on this line: {0}".format(line)
                    return
                archive_path = archive.group().replace("\"", "")
                try:
                    with open(archive_path) as archive_file:
                        started_parsing = False

                        lines_written = 0

                        for archive_line in archive_file:
                            archive_begin = archive_begin_expr.search(archive_line)
                            archive_end = archive_end_expr.search(archive_line)

                            # Error cases
                            if (started_parsing and archive_begin) or (not started_parsing and archive_end):
                                print "Malformed rib archive on this line: {0}".format(archive_line)
                                new_file.write(line)
                                break

                            # Edge case: One line that contains ArchiveBegin and ArchiveEnd
                            if not started_parsing and archive_begin and archive_end:
                                print "Rare case on line: {0}".format(archive_line)
                                start_index = archive_begin.span()[1] + 1
                                end_index = archive_end.span()[0] - 1

                                new_file.write(archive_line[start_index : end_index])
                                lines_written += 1
                                break

                            # One line that contains ArchiveBegin, signalling start of archive
                            if archive_begin:
                                print "Start of archive {0} on line {1}".format(archive_path, archive_line)
                                start_index = archive_begin.span()[1] + 1
                                start_index = start_index if start_index < len(line) else len(line) - 1

                                new_file.write(archive_line[start_index : ])
                                lines_written += 1
                                started_parsing = True

                            # One line that contains ArchiveEnd, signalling end of archive
                            elif archive_end:
                                print "End of archive {0} on line {1}".format(archive_path, archive_line)
                                end_index = archive_end.span()[0] - 1
                                end_index = end_index if end_index > 0 else 0

                                new_file.write(archive_line[ : end_index])
                                lines_written += 1
                                started_parsing = False

                            # The line is in between archive_start and archive_end, so write it
                            elif started_parsing:
                                print "Wrote line {0} from archive {1}".format(lines_written, archive_path)
                                new_file.write(archive_line)
                                lines_written += 1

                        print "{0} Total lines written from archive {1}".format(lines_written, archive_path)
                except IOError:
                    new_file.write(line)
                    print "Unable to open {0}".format(archive_path)
                except Error as e:
                    new_file.write(line)
                    print "Other error with {0}".format(e)





    #Remove original file
    remove(ribfile)

    #Move new file
    move(abs_path, ribfile)
