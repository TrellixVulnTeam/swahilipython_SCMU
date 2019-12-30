agiza sys

jaribu:
    agiza layout
tatizo ImportError:
    # Failed to agiza our package, which likely means we were started directly
    # Add the additional search path needed to locate our module.
    kutoka pathlib agiza Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

kutoka layout.main agiza main

sys.exit(int(main() ama 0))
