"""Small option parser for the emulated UNIX commands."""


class CommandError(ValueError):
    """A command has invalid options, operands, or values."""


def parse_flags(args: list[str], allowed: str):
    """Parse combined short flags and --; preserve operand order."""
    flags = set()
    operands = []
    options_enabled = True
    for arg in args:
        if options_enabled and arg == "--":
            options_enabled = False
        elif options_enabled and arg.startswith("-") and arg != "-":
            for flag in arg[1:]:
                if flag not in allowed:
                    raise CommandError(f"unsupported option: -{flag}")
                flags.add(flag)
        else:
            operands.append(arg)
    return flags, operands
