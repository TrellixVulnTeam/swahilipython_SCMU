#!/usr/bin/env python3

agiza argparse
agiza os
agiza pathlib
agiza zipfile
kutoka urllib.request agiza urlretrieve


eleza fetch_zip(commit_hash, zip_dir, *, org='python', binary=Uongo, verbose):
    repo = f'cpython-{"bin" ikiwa binary isipokua "source"}-deps'
    url = f'https://github.com/{org}/{repo}/archive/{commit_hash}.zip'
    reporthook = Tupu
    ikiwa verbose:
        reporthook = andika
    zip_dir.mkdir(parents=Kweli, exist_ok=Kweli)
    filename, headers = urlretrieve(
        url,
        zip_dir / f'{commit_hash}.zip',
        reporthook=reporthook,
    )
    rudisha filename


eleza extract_zip(externals_dir, zip_path):
    ukijumuisha zipfile.ZipFile(os.fspath(zip_path)) kama zf:
        zf.extractall(os.fspath(externals_dir))
        rudisha externals_dir / zf.namelist()[0].split('/')[0]


eleza parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-v', '--verbose', action='store_true')
    p.add_argument('-b', '--binary', action='store_true',
                   help='Is the dependency kwenye the binary repo?')
    p.add_argument('-O', '--organization',
                   help='Organization owning the deps repos', default='python')
    p.add_argument('-e', '--externals-dir', type=pathlib.Path,
                   help='Directory kwenye which to store dependencies',
                   default=pathlib.Path(__file__).parent.parent / 'externals')
    p.add_argument('tag',
                   help='tag of the dependency')
    rudisha p.parse_args()


eleza main():
    args = parse_args()
    zip_path = fetch_zip(
        args.tag,
        args.externals_dir / 'zips',
        org=args.organization,
        binary=args.binary,
        verbose=args.verbose,
    )
    final_name = args.externals_dir / args.tag
    extract_zip(args.externals_dir, zip_path).replace(final_name)


ikiwa __name__ == '__main__':
    main()
