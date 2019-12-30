agiza hashlib
agiza os
agiza sys

eleza main():
    filenames, hashes, sizes = [], [], []

    kila file kwenye sys.argv[1:]:
        ikiwa sio os.path.isfile(file):
            endelea

        ukijumuisha open(file, 'rb') kama f:
            data = f.read()
            md5 = hashlib.md5()
            md5.update(data)
            filenames.append(os.path.split(file)[1])
            hashes.append(md5.hexdigest())
            sizes.append(str(len(data)))

    andika('{:40s}  {:<32s}  {:<9s}'.format('File', 'MD5', 'Size'))
    kila f, h, s kwenye zip(filenames, hashes, sizes):
        andika('{:40s}  {:>32s}  {:>9s}'.format(f, h, s))



ikiwa __name__ == "__main__":
    sys.exit(int(main() ama 0))
