agiza sys
kutoka . agiza main

rc = 1
jaribu:
    main()
    rc = 0
tatizo Exception kama e:
    andika('Error: %s' % e, file=sys.stderr)
sys.exit(rc)
