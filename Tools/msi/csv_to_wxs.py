'''
Processes a CSV file containing a list of files into a WXS file with
components kila each listed file.

The CSV columns are:
    source of file, target kila file, group name

Usage::
    py txt_to_wxs.py [path to file list .csv] [path to destination .wxs]

This ni necessary to handle structures where some directories only
contain other directories. MSBuild ni sio able to generate the
Directory entries kwenye the WXS file correctly, kama it operates on files.
Python, however, can easily fill kwenye the gap.
'''

__author__ = "Steve Dower <steve.dower@microsoft.com>"

agiza csv
agiza re
agiza sys

kutoka collections agiza defaultdict
kutoka itertools agiza chain, zip_longest
kutoka pathlib agiza PureWindowsPath
kutoka uuid agiza uuid1

ID_CHAR_SUBS = {
    '-': '_',
    '+': '_P',
}

eleza make_id(path):
    rudisha re.sub(
        r'[^A-Za-z0-9_.]',
        lambda m: ID_CHAR_SUBS.get(m.group(0), '_'),
        str(path).rstrip('/\\'),
        flags=re.I
    )

DIRECTORIES = set()

eleza main(file_source, install_target):
    ukijumuisha open(file_source, 'r', newline='') kama f:
        files = list(csv.reader(f))

    assert len(files) == len(set(make_id(f[1]) kila f kwenye files)), "Duplicate file IDs exist"

    directories = defaultdict(set)
    cache_directories = defaultdict(set)
    groups = defaultdict(list)
    kila source, target, group, disk_id, condition kwenye files:
        target = PureWindowsPath(target)
        groups[group].append((source, target, disk_id, condition))

        ikiwa target.suffix.lower() kwenye {".py", ".pyw"}:
            cache_directories[group].add(target.parent)

        kila dirname kwenye target.parents:
            parent = make_id(dirname.parent)
            ikiwa parent na parent != '.':
                directories[parent].add(dirname.name)

    lines = [
        '<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">',
        '    <Fragment>',
    ]
    kila dir_parent kwenye sorted(directories):
        lines.append('        <DirectoryRef Id="{}">'.format(dir_parent))
        kila dir_name kwenye sorted(directories[dir_parent]):
            lines.append('            <Directory Id="{}_{}" Name="{}" />'.format(dir_parent, make_id(dir_name), dir_name))
        lines.append('        </DirectoryRef>')
    kila dir_parent kwenye (make_id(d) kila group kwenye cache_directories.values() kila d kwenye group):
        lines.append('        <DirectoryRef Id="{}">'.format(dir_parent))
        lines.append('            <Directory Id="{}___pycache__" Name="__pycache__" />'.format(dir_parent))
        lines.append('        </DirectoryRef>')
    lines.append('    </Fragment>')

    kila group kwenye sorted(groups):
        lines.extend([
            '    <Fragment>',
            '        <ComponentGroup Id="{}">'.format(group),
        ])
        kila source, target, disk_id, condition kwenye groups[group]:
            lines.append('            <Component Id="{}" Directory="{}" Guid="*">'.format(make_id(target), make_id(target.parent)))
            ikiwa condition:
                lines.append('                <Condition>{}</Condition>'.format(condition))

            ikiwa disk_id:
                lines.append('                <File Id="{}" Name="{}" Source="{}" DiskId="{}" />'.format(make_id(target), target.name, source, disk_id))
            isipokua:
                lines.append('                <File Id="{}" Name="{}" Source="{}" />'.format(make_id(target), target.name, source))
            lines.append('            </Component>')

        create_folders = {make_id(p) + "___pycache__" kila p kwenye cache_directories[group]}
        remove_folders = {make_id(p2) kila p1 kwenye cache_directories[group] kila p2 kwenye chain((p1,), p1.parents)}
        create_folders.discard(".")
        remove_folders.discard(".")
        ikiwa create_folders ama remove_folders:
            lines.append('            <Component Id="{}__pycache__folders" Directory="TARGETDIR" Guid="{}">'.format(group, uuid1()))
            lines.extend('                <CreateFolder Directory="{}" />'.format(p) kila p kwenye create_folders)
            lines.extend('                <RemoveFile Id="Remove_{0}_files" Name="*" On="uninstall" Directory="{0}" />'.format(p) kila p kwenye create_folders)
            lines.extend('                <RemoveFolder Id="Remove_{0}_folder" On="uninstall" Directory="{0}" />'.format(p) kila p kwenye create_folders | remove_folders)
            lines.append('            </Component>')

        lines.extend([
            '        </ComponentGroup>',
            '    </Fragment>',
        ])
    lines.append('</Wix>')

    # Check ikiwa the file matches. If so, we don't want to touch it so
    # that we can skip rebuilding.
    jaribu:
        ukijumuisha open(install_target, 'r') kama f:
            ikiwa all(x.rstrip('\r\n') == y kila x, y kwenye zip_longest(f, lines)):
                andika('File ni up to date')
                rudisha
    tatizo IOError:
        pita

    ukijumuisha open(install_target, 'w') kama f:
        f.writelines(line + '\n' kila line kwenye lines)
    andika('Wrote {} lines to {}'.format(len(lines), install_target))

ikiwa __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
