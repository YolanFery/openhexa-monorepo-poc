import re
import typing
from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    WORD = 1
    EXACT_WORD = 2
    FILTER = 3


@dataclass(frozen=True)
class Token:
    value: str
    type: TokenType


def tokenize(input_string: str) -> typing.List[Token]:
    tokens, accu, inside = [], "", False

    def push_token():
        nonlocal accu, tokens, inside
        if accu:
            t = TokenType.WORD
            if ":" in accu:
                t = TokenType.FILTER
            elif inside:
                t = TokenType.EXACT_WORD
            tokens.append(Token(value=accu.lower(), type=t))
            accu = ""

    def accumulate(c):
        nonlocal accu
        accu += c

    for c in input_string:
        if c == " ":
            if inside:
                accumulate(c)
            else:
                push_token()
        elif c == '"':
            push_token()
            inside = not inside
        else:
            accumulate(c)
    push_token()
    return tokens


def normalize_search_index(raw_search: str) -> str:
    return re.sub(r"( +)", " ", raw_search.replace("\t", " ").lower()).strip()
