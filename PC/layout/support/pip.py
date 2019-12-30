"""
Extraction na file list generation kila pip.
"""

__author__ = "Steve Dower <steve.dower@python.org>"
__version__ = "3.8"


agiza os
agiza shutil
agiza subprocess
agiza sys

kutoka .filesets agiza *

__all__ = ["extract_pip_files", "get_pip_layout"]


eleza get_pip_dir(ns):
    ikiwa ns.copy:
        ikiwa ns.zip_lib:
            rudisha ns.copy / "packages"
        rudisha ns.copy / "Lib" / "site-packages"
    isipokua:
        rudisha ns.temp / "packages"


eleza get_pip_layout(ns):
    pip_dir = get_pip_dir(ns)
    ikiwa sio pip_dir.is_dir():
        log_warning("Failed to find {} - pip will sio be included", pip_dir)
    isipokua:
        pkg_root = "packages/{}" ikiwa ns.zip_lib isipokua "Lib/site-packages/{}"
        kila dest, src kwenye rglob(pip_dir, "**/*"):
            tuma pkg_root.format(dest), src
        ikiwa ns.include_pip_user:
            content = "\n".join(
                "[{}]\nuser=yes".format(n)
                kila n kwenye ["install", "uninstall", "freeze", "list"]
            )
            tuma "pip.ini", ("pip.ini", content.encode())


eleza extract_pip_files(ns):
    dest = get_pip_dir(ns)
    jaribu:
        dest.mkdir(parents=Kweli, exist_ok=Uongo)
    tatizo IOError:
        rudisha

    src = ns.source / "Lib" / "ensurepip" / "_bundled"

    ns.temp.mkdir(parents=Kweli, exist_ok=Kweli)
    wheels = [shutil.copy(whl, ns.temp) kila whl kwenye src.glob("*.whl")]
    search_path = os.pathsep.join(wheels)
    ikiwa os.environ.get("PYTHONPATH"):
        search_path += ";" + os.environ["PYTHONPATH"]

    env = os.environ.copy()
    env["PYTHONPATH"] = search_path

    output = subprocess.check_output(
        [
            sys.executable,
            "-m",
            "pip",
            "--no-color",
            "install",
            "pip",
            "setuptools",
            "--upgrade",
            "--target",
            str(dest),
            "--no-index",
            "--no-compile",
            "--no-cache-dir",
            "-f",
            str(src),
            "--only-binary",
            ":all:",
        ],
        env=env,
    )

    jaribu:
        shutil.rmtree(dest / "bin")
    tatizo OSError:
        pita

    kila file kwenye wheels:
        jaribu:
            os.remove(file)
        tatizo OSError:
            pita
