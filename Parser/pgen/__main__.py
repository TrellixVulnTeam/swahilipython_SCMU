agiza argparse

kutoka .pgen agiza ParserGenerator


eleza main():
    parser = argparse.ArgumentParser(description="Parser generator main program.")
    parser.add_argument(
        "grammar", type=str, help="The file ukijumuisha the grammar definition kwenye EBNF format"
    )
    parser.add_argument(
        "tokens", type=str, help="The file ukijumuisha the token definitions"
    )
    parser.add_argument(
        "graminit_h",
        type=argparse.FileType('w'),
        help="The path to write the grammar's non-terminals kama #defines",
    )
    parser.add_argument(
        "graminit_c",
        type=argparse.FileType('w'),
        help="The path to write the grammar kama initialized data",
    )

    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    p = ParserGenerator(args.grammar, args.tokens, verbose=args.verbose)
    grammar = p.make_grammar()
    grammar.produce_graminit_h(args.graminit_h.write)
    grammar.produce_graminit_c(args.graminit_c.write)


ikiwa __name__ == "__main__":
    main()
