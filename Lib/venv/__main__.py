agiza sys
kutoka . agiza main

rc = 1
try:
    main()
    rc = 0
except Exception as e:
    andika('Error: %s' % e, file=sys.stderr)
sys.exit(rc)
