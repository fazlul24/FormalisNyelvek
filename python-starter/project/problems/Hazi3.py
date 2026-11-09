from project.problem import Problem


class MinimizeProblem(Problem):

    def initialize_parser(self, parser):
        parser.add_argument(
            '--mini',
            action='store_true',
            help='minimize the given DFA'
        )

    def is_chosen_problem(self, args):
        return getattr(args, 'mini', False)

    def run(self, args):
        # ---------- Beolvasás ----------
        with open(args.input, 'r') as f:
            lines = [line.strip() for line in f if line.strip() != '']

        states = lines[0].split()
        alphabet = lines[1].split()
        start_state = lines[2].strip()
        accept_states = set(lines[3].split())

        valid_states = set(states)
        valid_symbols = set(alphabet)

        # ---------- Hibakezelés ----------
        if start_state not in valid_states:
            raise ValueError(f"Invalid start state: {start_state}")
        for s in accept_states:
            if s not in valid_states:
                raise ValueError(f"Invalid accept state: {s}")

        transitions = {}  # state -> symbol -> target
        for line in lines[4:]:
            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"Invalid transition line: '{line}'")
            src, sym, dst = parts
            if src not in valid_states:
                raise ValueError(f"Unknown state in transition: '{src}'")
            if dst not in valid_states:
                raise ValueError(f"Unknown state in transition: '{dst}'")
            if sym not in valid_symbols:
                raise ValueError(f"Unknown symbol in transition: '{sym}'")
            if src in transitions and sym in transitions[src]:
                raise ValueError(
                    f"Non-deterministic transition for ({src}, {sym})"
                )
            transitions.setdefault(src, {})[sym] = dst

        # ---------- Elérhetetlen állapotok eltávolítása ----------
        reachable = set()
        stack = [start_state]
        while stack:
            st = stack.pop()
            if st in reachable:
                continue
            reachable.add(st)
            for sym in alphabet:
                nxt = transitions.get(st, {}).get(sym)
                if nxt is not None and nxt not in reachable:
                    stack.append(nxt)

        working_states = [s for s in states if s in reachable]
        accept_set = set(s for s in accept_states if s in reachable)
        non_accept_set = set(working_states) - accept_set

        # ---------- Kezdeti partició ----------
        partition = []
        if accept_set:
            partition.append(frozenset(accept_set))
        if non_accept_set:
            partition.append(frozenset(non_accept_set))

        def find_class(state):
            for i, cls in enumerate(partition):
                if state in cls:
                    return i
            return -1

        # ---------- Finomítás (Moore) ----------
        changed = True
        while changed:
            changed = False
            new_partition = []
            for cls in partition:
                groups = {}
                for st in sorted(cls):
                    sig = tuple(
                        find_class(transitions[st][sym])
                        if sym in transitions.get(st, {})
                        else -1
                        for sym in alphabet
                    )
                    groups.setdefault(sig, set()).add(st)

                if len(groups) == 1:
                    new_partition.append(cls)
                else:
                    changed = True
                    for grp in groups.values():
                        new_partition.append(frozenset(grp))
            partition = new_partition

        # ---------- Új állapotnevek ----------
        original_index = {s: i for i, s in enumerate(lines[0].split())}

        state_class = {}
        for cls in partition:
            for st in cls:
                state_class[st] = cls

        class_name = {}
        for cls in partition:
            min_idx = min(original_index[s] for s in cls)
            class_name[cls] = f"s{min_idx}"

        def name_of(st):
            return class_name[state_class[st]]

        # ---------- Kimeneti állapotok ----------
        sorted_classes = sorted(
            partition,
            key=lambda c: int(class_name[c][1:])
        )
        out_state_names = [class_name[c] for c in sorted_classes]

        out_accept = sorted(
            set(name_of(s) for s in accept_states if s in reachable),
            key=lambda n: int(n[1:])
        )
        out_start = name_of(start_state)

        # ---------- Átmenetek ----------
        out_transitions = []
        for cls in sorted_classes:
            src_name = class_name[cls]
            rep = min(cls, key=lambda s: original_index[s])
            for sym in alphabet:
                dst = transitions.get(rep, {}).get(sym)
                if dst is None:
                    continue
                out_transitions.append((src_name, sym, name_of(dst)))

        out_transitions.sort(key=lambda t: (
            int(t[0][1:]),
            t[1],
            int(t[2][1:])
        ))

        # ---------- Kiírás ----------
        with open(args.output, 'w') as f:
            f.write(" ".join(out_state_names) + "\n")
            f.write(" ".join(sorted(alphabet)) + "\n")
            f.write(out_start + "\n")
            f.write(" ".join(out_accept) + "\n")
            for src, sym, dst in out_transitions:
                f.write(f"{src} {sym} {dst}\n")

###veg