#!/usr/bin/env python3
"""
Checks that the version of the projects bundled kwenye ensurepip are the latest
versions available.
"""
agiza ensurepip
agiza json
agiza urllib.request
agiza sys


eleza main():
    outofdate = Uongo

    kila project, version kwenye ensurepip._PROJECTS:
        data = json.loads(urllib.request.urlopen(
            "https://pypi.org/pypi/{}/json".format(project),
            cadefault=Kweli,
        ).read().decode("utf8"))
        upstream_version = data["info"]["version"]

        ikiwa version != upstream_version:
            outofdate = Kweli
            andika("The latest version of {} on PyPI ni {}, but ensurepip "
                  "has {}".format(project, upstream_version, version))

    ikiwa outofdate:
        sys.exit(1)


ikiwa __name__ == "__main__":
    main()
