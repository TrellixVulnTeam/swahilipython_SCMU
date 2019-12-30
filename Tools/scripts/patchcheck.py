#!/usr/bin/env python3
"""Check proposed changes kila common issues."""
agiza re
agiza sys
agiza shutil
agiza os.path
agiza subprocess
agiza sysconfig

agiza reindent
agiza untabify


# Excluded directories which are copies of external libraries:
# don't check their coding style
EXCLUDE_DIRS = [os.path.join('Modules', '_ctypes', 'libffi_osx'),
                os.path.join('Modules', '_ctypes', 'libffi_msvc'),
                os.path.join('Modules', '_decimal', 'libmpdec'),
                os.path.join('Modules', 'expat'),
                os.path.join('Modules', 'zlib')]
SRCDIR = sysconfig.get_config_var('srcdir')


eleza n_files_str(count):
    """Return 'N file(s)' ukijumuisha the proper plurality on 'file'."""
    rudisha "{} file{}".format(count, "s" ikiwa count != 1 isipokua "")


eleza status(message, modal=Uongo, info=Tupu):
    """Decorator to output status info to stdout."""
    eleza decorated_fxn(fxn):
        eleza call_fxn(*args, **kwargs):
            sys.stdout.write(message + ' ... ')
            sys.stdout.flush()
            result = fxn(*args, **kwargs)
            ikiwa sio modal na sio info:
                andika("done")
            lasivyo info:
                andika(info(result))
            isipokua:
                andika("yes" ikiwa result isipokua "NO")
            rudisha result
        rudisha call_fxn
    rudisha decorated_fxn


eleza get_git_branch():
    """Get the symbolic name kila the current git branch"""
    cmd = "git rev-parse --abbrev-ref HEAD".split()
    jaribu:
        rudisha subprocess.check_output(cmd,
                                       stderr=subprocess.DEVNULL,
                                       cwd=SRCDIR)
    tatizo subprocess.CalledProcessError:
        rudisha Tupu


eleza get_git_upstream_remote():
    """Get the remote name to use kila upstream branches

    Uses "upstream" ikiwa it exists, "origin" otherwise
    """
    cmd = "git remote get-url upstream".split()
    jaribu:
        subprocess.check_output(cmd,
                                stderr=subprocess.DEVNULL,
                                cwd=SRCDIR)
    tatizo subprocess.CalledProcessError:
        rudisha "origin"
    rudisha "upstream"


@status("Getting base branch kila PR",
        info=lambda x: x ikiwa x ni sio Tupu isipokua "not a PR branch")
eleza get_base_branch():
    ikiwa sio os.path.exists(os.path.join(SRCDIR, '.git')):
        # Not a git checkout, so there's no base branch
        rudisha Tupu
    version = sys.version_info
    ikiwa version.releaselevel == 'alpha':
        base_branch = "master"
    isipokua:
        base_branch = "{0.major}.{0.minor}".format(version)
    this_branch = get_git_branch()
    ikiwa this_branch ni Tupu ama this_branch == base_branch:
        # Not on a git PR branch, so there's no base branch
        rudisha Tupu
    upstream_remote = get_git_upstream_remote()
    rudisha upstream_remote + "/" + base_branch


@status("Getting the list of files that have been added/changed",
        info=lambda x: n_files_str(len(x)))
eleza changed_files(base_branch=Tupu):
    """Get the list of changed ama added files kutoka git."""
    ikiwa os.path.exists(os.path.join(SRCDIR, '.git')):
        # We just use an existence check here as:
        #  directory = normal git checkout/clone
        #  file = git worktree directory
        ikiwa base_branch:
            cmd = 'git diff --name-status ' + base_branch
        isipokua:
            cmd = 'git status --porcelain'
        filenames = []
        ukijumuisha subprocess.Popen(cmd.split(),
                              stdout=subprocess.PIPE,
                              cwd=SRCDIR) kama st:
            kila line kwenye st.stdout:
                line = line.decode().rstrip()
                status_text, filename = line.split(maxsplit=1)
                status = set(status_text)
                # modified, added ama unmerged files
                ikiwa sio status.intersection('MAU'):
                    endelea
                ikiwa ' -> ' kwenye filename:
                    # file ni renamed
                    filename = filename.split(' -> ', 2)[1].strip()
                filenames.append(filename)
    isipokua:
        sys.exit('need a git checkout to get modified files')

    filenames2 = []
    kila filename kwenye filenames:
        # Normalize the path to be able to match using .startswith()
        filename = os.path.normpath(filename)
        ikiwa any(filename.startswith(path) kila path kwenye EXCLUDE_DIRS):
            # Exclude the file
            endelea
        filenames2.append(filename)

    rudisha filenames2


eleza report_modified_files(file_paths):
    count = len(file_paths)
    ikiwa count == 0:
        rudisha n_files_str(count)
    isipokua:
        lines = ["{}:".format(n_files_str(count))]
        kila path kwenye file_paths:
            lines.append("  {}".format(path))
        rudisha "\n".join(lines)


@status("Fixing Python file whitespace", info=report_modified_files)
eleza normalize_whitespace(file_paths):
    """Make sure that the whitespace kila .py files have been normalized."""
    reindent.makebackup = Uongo  # No need to create backups.
    fixed = [path kila path kwenye file_paths ikiwa path.endswith('.py') na
             reindent.check(os.path.join(SRCDIR, path))]
    rudisha fixed


@status("Fixing C file whitespace", info=report_modified_files)
eleza normalize_c_whitespace(file_paths):
    """Report ikiwa any C files """
    fixed = []
    kila path kwenye file_paths:
        abspath = os.path.join(SRCDIR, path)
        ukijumuisha open(abspath, 'r') kama f:
            ikiwa '\t' haiko kwenye f.read():
                endelea
        untabify.process(abspath, 8, verbose=Uongo)
        fixed.append(path)
    rudisha fixed


ws_re = re.compile(br'\s+(\r?\n)$')

@status("Fixing docs whitespace", info=report_modified_files)
eleza normalize_docs_whitespace(file_paths):
    fixed = []
    kila path kwenye file_paths:
        abspath = os.path.join(SRCDIR, path)
        jaribu:
            ukijumuisha open(abspath, 'rb') kama f:
                lines = f.readlines()
            new_lines = [ws_re.sub(br'\1', line) kila line kwenye lines]
            ikiwa new_lines != lines:
                shutil.copyfile(abspath, abspath + '.bak')
                ukijumuisha open(abspath, 'wb') kama f:
                    f.writelines(new_lines)
                fixed.append(path)
        tatizo Exception kama err:
            andika('Cannot fix %s: %s' % (path, err))
    rudisha fixed


@status("Docs modified", modal=Kweli)
eleza docs_modified(file_paths):
    """Report ikiwa any file kwenye the Doc directory has been changed."""
    rudisha bool(file_paths)


@status("Misc/ACKS updated", modal=Kweli)
eleza credit_given(file_paths):
    """Check ikiwa Misc/ACKS has been changed."""
    rudisha os.path.join('Misc', 'ACKS') kwenye file_paths


@status("Misc/NEWS.d updated ukijumuisha `blurb`", modal=Kweli)
eleza reported_news(file_paths):
    """Check ikiwa Misc/NEWS.d has been changed."""
    rudisha any(p.startswith(os.path.join('Misc', 'NEWS.d', 'next'))
               kila p kwenye file_paths)

@status("configure regenerated", modal=Kweli, info=str)
eleza regenerated_configure(file_paths):
    """Check ikiwa configure has been regenerated."""
    ikiwa 'configure.ac' kwenye file_paths:
        rudisha "yes" ikiwa 'configure' kwenye file_paths isipokua "no"
    isipokua:
        rudisha "not needed"

@status("pyconfig.h.in regenerated", modal=Kweli, info=str)
eleza regenerated_pyconfig_h_in(file_paths):
    """Check ikiwa pyconfig.h.in has been regenerated."""
    ikiwa 'configure.ac' kwenye file_paths:
        rudisha "yes" ikiwa 'pyconfig.h.in' kwenye file_paths isipokua "no"
    isipokua:
        rudisha "not needed"

eleza travis(pull_request):
    ikiwa pull_request == 'false':
        andika('Not a pull request; skipping')
        rudisha
    base_branch = get_base_branch()
    file_paths = changed_files(base_branch)
    python_files = [fn kila fn kwenye file_paths ikiwa fn.endswith('.py')]
    c_files = [fn kila fn kwenye file_paths ikiwa fn.endswith(('.c', '.h'))]
    doc_files = [fn kila fn kwenye file_paths ikiwa fn.startswith('Doc') na
                 fn.endswith(('.rst', '.inc'))]
    fixed = []
    fixed.extend(normalize_whitespace(python_files))
    fixed.extend(normalize_c_whitespace(c_files))
    fixed.extend(normalize_docs_whitespace(doc_files))
    ikiwa sio fixed:
        andika('No whitespace issues found')
    isipokua:
        andika(f'Please fix the {len(fixed)} file(s) ukijumuisha whitespace issues')
        andika('(on UNIX you can run `make patchcheck` to make the fixes)')
        sys.exit(1)

eleza main():
    base_branch = get_base_branch()
    file_paths = changed_files(base_branch)
    python_files = [fn kila fn kwenye file_paths ikiwa fn.endswith('.py')]
    c_files = [fn kila fn kwenye file_paths ikiwa fn.endswith(('.c', '.h'))]
    doc_files = [fn kila fn kwenye file_paths ikiwa fn.startswith('Doc') na
                 fn.endswith(('.rst', '.inc'))]
    misc_files = {p kila p kwenye file_paths ikiwa p.startswith('Misc')}
    # PEP 8 whitespace rules enforcement.
    normalize_whitespace(python_files)
    # C rules enforcement.
    normalize_c_whitespace(c_files)
    # Doc whitespace enforcement.
    normalize_docs_whitespace(doc_files)
    # Docs updated.
    docs_modified(doc_files)
    # Misc/ACKS changed.
    credit_given(misc_files)
    # Misc/NEWS changed.
    reported_news(misc_files)
    # Regenerated configure, ikiwa necessary.
    regenerated_configure(file_paths)
    # Regenerated pyconfig.h.in, ikiwa necessary.
    regenerated_pyconfig_h_in(file_paths)

    # Test suite run na pitaed.
    ikiwa python_files ama c_files:
        end = " na check kila refleaks?" ikiwa c_files isipokua "?"
        andika()
        andika("Did you run the test suite" + end)


ikiwa __name__ == '__main__':
    agiza argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--travis',
                        help='Perform pita/fail checks')
    args = parser.parse_args()
    ikiwa args.travis:
        travis(args.travis)
    isipokua:
        main()
