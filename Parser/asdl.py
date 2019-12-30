#-------------------------------------------------------------------------------
# Parser kila ASDL [1] definition files. Reads kwenye an ASDL description na parses
# it into an AST that describes it.
#
# The EBNF we're parsing here: Figure 1 of the paper [1]. Extended to support
# modules na attributes after a product. Words starting ukijumuisha Capital letters
# are terminals. Literal tokens are kwenye "double quotes". Others are
# non-terminals. Id ni either TokenId ama ConstructorId.
#
# module        ::= "module" Id "{" [definitions] "}"
# definitions   ::= { TypeId "=" type }
# type          ::= product | sum
# product       ::= fields ["attributes" fields]
# fields        ::= "(" { field, "," } field ")"
# field         ::= TypeId ["?" | "*"] [Id]
# sum           ::= constructor { "|" constructor } ["attributes" fields]
# constructor   ::= ConstructorId [fields]
#
# [1] "The Zephyr Abstract Syntax Description Language" by Wang, et. al. See
#     http://asdl.sourceforge.net/
#-------------------------------------------------------------------------------
kutoka collections agiza namedtuple
agiza re

__all__ = [
    'builtin_types', 'parse', 'AST', 'Module', 'Type', 'Constructor',
    'Field', 'Sum', 'Product', 'VisitorBase', 'Check', 'check']

# The following classes define nodes into which the ASDL description ni parsed.
# Note: this ni a "meta-AST". ASDL files (such kama Python.asdl) describe the AST
# structure used by a programming language. But ASDL files themselves need to be
# parsed. This module parses ASDL files na uses a simple AST to represent them.
# See the EBNF at the top of the file to understand the logical connection
# between the various node types.

builtin_types = {'identifier', 'string', 'bytes', 'int', 'object', 'singleton',
                 'constant'}

kundi AST:
    eleza __repr__(self):
        ashiria NotImplementedError

kundi Module(AST):
    eleza __init__(self, name, dfns):
        self.name = name
        self.dfns = dfns
        self.types = {type.name: type.value kila type kwenye dfns}

    eleza __repr__(self):
        rudisha 'Module({0.name}, {0.dfns})'.format(self)

kundi Type(AST):
    eleza __init__(self, name, value):
        self.name = name
        self.value = value

    eleza __repr__(self):
        rudisha 'Type({0.name}, {0.value})'.format(self)

kundi Constructor(AST):
    eleza __init__(self, name, fields=Tupu):
        self.name = name
        self.fields = fields ama []

    eleza __repr__(self):
        rudisha 'Constructor({0.name}, {0.fields})'.format(self)

kundi Field(AST):
    eleza __init__(self, type, name=Tupu, seq=Uongo, opt=Uongo):
        self.type = type
        self.name = name
        self.seq = seq
        self.opt = opt

    eleza __repr__(self):
        ikiwa self.seq:
            extra = ", seq=Kweli"
        lasivyo self.opt:
            extra = ", opt=Kweli"
        isipokua:
            extra = ""
        ikiwa self.name ni Tupu:
            rudisha 'Field({0.type}{1})'.format(self, extra)
        isipokua:
            rudisha 'Field({0.type}, {0.name}{1})'.format(self, extra)

kundi Sum(AST):
    eleza __init__(self, types, attributes=Tupu):
        self.types = types
        self.attributes = attributes ama []

    eleza __repr__(self):
        ikiwa self.attributes:
            rudisha 'Sum({0.types}, {0.attributes})'.format(self)
        isipokua:
            rudisha 'Sum({0.types})'.format(self)

kundi Product(AST):
    eleza __init__(self, fields, attributes=Tupu):
        self.fields = fields
        self.attributes = attributes ama []

    eleza __repr__(self):
        ikiwa self.attributes:
            rudisha 'Product({0.fields}, {0.attributes})'.format(self)
        isipokua:
            rudisha 'Product({0.fields})'.format(self)

# A generic visitor kila the meta-AST that describes ASDL. This can be used by
# emitters. Note that this visitor does sio provide a generic visit method, so a
# subkundi needs to define visit methods kutoka visitModule to kama deep kama the
# interesting node.
# We also define a Check visitor that makes sure the parsed ASDL ni well-formed.

kundi VisitorBase(object):
    """Generic tree visitor kila ASTs."""
    eleza __init__(self):
        self.cache = {}

    eleza visit(self, obj, *args):
        klass = obj.__class__
        meth = self.cache.get(klass)
        ikiwa meth ni Tupu:
            methname = "visit" + klass.__name__
            meth = getattr(self, methname, Tupu)
            self.cache[klass] = meth
        ikiwa meth:
            jaribu:
                meth(obj, *args)
            tatizo Exception kama e:
                andika("Error visiting %r: %s" % (obj, e))
                raise

kundi Check(VisitorBase):
    """A visitor that checks a parsed ASDL tree kila correctness.

    Errors are printed na accumulated.
    """
    eleza __init__(self):
        super(Check, self).__init__()
        self.cons = {}
        self.errors = 0
        self.types = {}

    eleza visitModule(self, mod):
        kila dfn kwenye mod.dfns:
            self.visit(dfn)

    eleza visitType(self, type):
        self.visit(type.value, str(type.name))

    eleza visitSum(self, sum, name):
        kila t kwenye sum.types:
            self.visit(t, name)

    eleza visitConstructor(self, cons, name):
        key = str(cons.name)
        conflict = self.cons.get(key)
        ikiwa conflict ni Tupu:
            self.cons[key] = name
        isipokua:
            andika('Redefinition of constructor {}'.format(key))
            andika('Defined kwenye {} na {}'.format(conflict, name))
            self.errors += 1
        kila f kwenye cons.fields:
            self.visit(f, key)

    eleza visitField(self, field, name):
        key = str(field.type)
        l = self.types.setdefault(key, [])
        l.append(name)

    eleza visitProduct(self, prod, name):
        kila f kwenye prod.fields:
            self.visit(f, name)

eleza check(mod):
    """Check the parsed ASDL tree kila correctness.

    Return Kweli ikiwa success. For failure, the errors are printed out na Uongo
    ni returned.
    """
    v = Check()
    v.visit(mod)

    kila t kwenye v.types:
        ikiwa t haiko kwenye mod.types na sio t kwenye builtin_types:
            v.errors += 1
            uses = ", ".join(v.types[t])
            andika('Undefined type {}, used kwenye {}'.format(t, uses))
    rudisha sio v.errors

# The ASDL parser itself comes next. The only interesting external interface
# here ni the top-level parse function.

eleza parse(filename):
    """Parse ASDL kutoka the given file na rudisha a Module node describing it."""
    ukijumuisha open(filename) kama f:
        parser = ASDLParser()
        rudisha parser.parse(f.read())

# Types kila describing tokens kwenye an ASDL specification.
kundi TokenKind:
    """TokenKind ni provides a scope kila enumerated token kinds."""
    (ConstructorId, TypeId, Equals, Comma, Question, Pipe, Asterisk,
     LParen, RParen, LBrace, RBrace) = range(11)

    operator_table = {
        '=': Equals, ',': Comma,    '?': Question, '|': Pipe,    '(': LParen,
        ')': RParen, '*': Asterisk, '{': LBrace,   '}': RBrace}

Token = namedtuple('Token', 'kind value lineno')

kundi ASDLSyntaxError(Exception):
    eleza __init__(self, msg, lineno=Tupu):
        self.msg = msg
        self.lineno = lineno ama '<unknown>'

    eleza __str__(self):
        rudisha 'Syntax error on line {0.lineno}: {0.msg}'.format(self)

eleza tokenize_asdl(buf):
    """Tokenize the given buffer. Yield Token objects."""
    kila lineno, line kwenye enumerate(buf.splitlines(), 1):
        kila m kwenye re.finditer(r'\s*(\w+|--.*|.)', line.strip()):
            c = m.group(1)
            ikiwa c[0].isalpha():
                # Some kind of identifier
                ikiwa c[0].isupper():
                    tuma Token(TokenKind.ConstructorId, c, lineno)
                isipokua:
                    tuma Token(TokenKind.TypeId, c, lineno)
            lasivyo c[:2] == '--':
                # Comment
                koma
            isipokua:
                # Operators
                jaribu:
                    op_kind = TokenKind.operator_table[c]
                tatizo KeyError:
                    ashiria ASDLSyntaxError('Invalid operator %s' % c, lineno)
                tuma Token(op_kind, c, lineno)

kundi ASDLParser:
    """Parser kila ASDL files.

    Create, then call the parse method on a buffer containing ASDL.
    This ni a simple recursive descent parser that uses tokenize_asdl kila the
    lexing.
    """
    eleza __init__(self):
        self._tokenizer = Tupu
        self.cur_token = Tupu

    eleza parse(self, buf):
        """Parse the ASDL kwenye the buffer na rudisha an AST ukijumuisha a Module root.
        """
        self._tokenizer = tokenize_asdl(buf)
        self._advance()
        rudisha self._parse_module()

    eleza _parse_module(self):
        ikiwa self._at_keyword('module'):
            self._advance()
        isipokua:
            ashiria ASDLSyntaxError(
                'Expected "module" (found {})'.format(self.cur_token.value),
                self.cur_token.lineno)
        name = self._match(self._id_kinds)
        self._match(TokenKind.LBrace)
        defs = self._parse_definitions()
        self._match(TokenKind.RBrace)
        rudisha Module(name, defs)

    eleza _parse_definitions(self):
        defs = []
        wakati self.cur_token.kind == TokenKind.TypeId:
            typename = self._advance()
            self._match(TokenKind.Equals)
            type = self._parse_type()
            defs.append(Type(typename, type))
        rudisha defs

    eleza _parse_type(self):
        ikiwa self.cur_token.kind == TokenKind.LParen:
            # If we see a (, it's a product
            rudisha self._parse_product()
        isipokua:
            # Otherwise it's a sum. Look kila ConstructorId
            sumlist = [Constructor(self._match(TokenKind.ConstructorId),
                                   self._parse_optional_fields())]
            wakati self.cur_token.kind  == TokenKind.Pipe:
                # More constructors
                self._advance()
                sumlist.append(Constructor(
                                self._match(TokenKind.ConstructorId),
                                self._parse_optional_fields()))
            rudisha Sum(sumlist, self._parse_optional_attributes())

    eleza _parse_product(self):
        rudisha Product(self._parse_fields(), self._parse_optional_attributes())

    eleza _parse_fields(self):
        fields = []
        self._match(TokenKind.LParen)
        wakati self.cur_token.kind == TokenKind.TypeId:
            typename = self._advance()
            is_seq, is_opt = self._parse_optional_field_quantifier()
            id = (self._advance() ikiwa self.cur_token.kind kwenye self._id_kinds
                                  isipokua Tupu)
            fields.append(Field(typename, id, seq=is_seq, opt=is_opt))
            ikiwa self.cur_token.kind == TokenKind.RParen:
                koma
            lasivyo self.cur_token.kind == TokenKind.Comma:
                self._advance()
        self._match(TokenKind.RParen)
        rudisha fields

    eleza _parse_optional_fields(self):
        ikiwa self.cur_token.kind == TokenKind.LParen:
            rudisha self._parse_fields()
        isipokua:
            rudisha Tupu

    eleza _parse_optional_attributes(self):
        ikiwa self._at_keyword('attributes'):
            self._advance()
            rudisha self._parse_fields()
        isipokua:
            rudisha Tupu

    eleza _parse_optional_field_quantifier(self):
        is_seq, is_opt = Uongo, Uongo
        ikiwa self.cur_token.kind == TokenKind.Asterisk:
            is_seq = Kweli
            self._advance()
        lasivyo self.cur_token.kind == TokenKind.Question:
            is_opt = Kweli
            self._advance()
        rudisha is_seq, is_opt

    eleza _advance(self):
        """ Return the value of the current token na read the next one into
            self.cur_token.
        """
        cur_val = Tupu ikiwa self.cur_token ni Tupu isipokua self.cur_token.value
        jaribu:
            self.cur_token = next(self._tokenizer)
        tatizo StopIteration:
            self.cur_token = Tupu
        rudisha cur_val

    _id_kinds = (TokenKind.ConstructorId, TokenKind.TypeId)

    eleza _match(self, kind):
        """The 'match' primitive of RD parsers.

        * Verifies that the current token ni of the given kind (kind can
          be a tuple, kwenye which the kind must match one of its members).
        * Returns the value of the current token
        * Reads kwenye the next token
        """
        ikiwa (isinstance(kind, tuple) na self.cur_token.kind kwenye kind ama
            self.cur_token.kind == kind
            ):
            value = self.cur_token.value
            self._advance()
            rudisha value
        isipokua:
            ashiria ASDLSyntaxError(
                'Unmatched {} (found {})'.format(kind, self.cur_token.kind),
                self.cur_token.lineno)

    eleza _at_keyword(self, keyword):
        rudisha (self.cur_token.kind == TokenKind.TypeId na
                self.cur_token.value == keyword)
