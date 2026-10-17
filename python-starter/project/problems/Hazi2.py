from project.problem import Problem


class DeterminizeProblem(Problem):

    def initialize_parser(self, parser):
        parser.add_argument(
            '--det',
            action='store_true',
            help='determinize the given NFA'
        )

    def is_chosen_problem(self, args):
        return getattr(args, 'det', False)

    def run(self, args):
        # ---------- Beolvasás ----------
        with open(args.input, 'r') as f:
            lines = [line.strip() for line in f if line.strip() != '']

        states = lines[0].split()
        alphabet = lines[1].split()
        start_state = lines[2].strip()
        accept_states = set(lines[3].split())

        # ---------- Hibakezelés ----------
        valid_states = set(states)
        valid_symbols = set(alphabet)

        if start_state not in valid_states:
            raise ValueError(f"Invalid start state: {start_state}")
        for s in accept_states:
            if s not in valid_states:
                raise ValueError(f"Invalid accept state: {s}")

        # NFA átmeneti tábla: (state, symbol) -> set of target states
        nfa_transitions = {}
        for line in lines[4:]:
            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"Invalid transition line: '{line}'")
            from_state, symbol, to_state = parts
            if from_state not in valid_states:
                raise ValueError(f"Unknown state in transition: '{from_state}'")
            if to_state not in valid_states:
                raise ValueError(f"Unknown state in transition: '{to_state}'")
            if symbol not in valid_symbols:
                raise ValueError(f"Unknown symbol in transition: '{symbol}'")

            nfa_transitions.setdefault((from_state, symbol), set()).add(to_state)

        # ---------- Részhalmaz-konstrukció ----------
        # A DFA állapotai halmazok. Kezdő: {start_state}
        start_set = frozenset([start_state])

        # BFS-szerű felfedezés, hogy a sorrend determinisztikus legyen
        dfa_states = [start_set]
        dfa_state_index = {start_set: 0}
        dfa_transitions = {}  # (index, symbol) -> target index

        queue = [start_set]
        while queue:
            current_set = queue.pop(0)
            current_idx = dfa_state_index[current_set]

            for symbol in alphabet:
                # Összegyűjtjük a célállapotokat
                targets = set()
                for state in current_set:
                    targets |= nfa_transitions.get((state, symbol), set())

                if not targets:
                    continue  # nincs átmenet, nem írjuk ki

                target_set = frozenset(targets)
                if target_set not in dfa_state_index:
                    dfa_state_index[target_set] = len(dfa_states)
                    dfa_states.append(target_set)
                    queue.append(target_set)

                dfa_transitions[(current_idx, symbol)] = dfa_state_index[target_set]

        # ---------- DFA állapotok újraszámozása s0, s1, ... ----------
        # A feladat példái szerint az s0 a kezdőállapot.
        # A BFS sorrend pontosan ezt adja: s0 = {start_state}.

        # Elfogadó DFA állapotok: azok a halmazok, amelyek tartalmaznak
        # legalább egy NFA elfogadó állapotot.
        dfa_accept_indices = sorted(
            i for i, s in enumerate(dfa_states) if s & accept_states
        )

        # ---------- Kiírás ----------
        # 1. sor: állapotok
        state_names = [f"s{i}" for i in range(len(dfa_states))]

        # 2. sor: ábécé (a bemeneti sorrend szerint; a feladat példáiban
        # az ábécé eleve ábécé-sorrendben van, de biztos ami biztos:)
        out_alphabet = sorted(alphabet)

        # 3. sor: kezdőállapot
        out_start = "s0"

        # 4. sor: elfogadó állapotok
        out_accept = sorted(f"s{i}" for i in dfa_accept_indices)

        # Átmenetek: csomópont szerint, majd élcímke szerint, majd cél szerint
        out_transitions = []
        # Végigmegyünk a DFA állapotokon s0..sn sorrendben
        for idx in range(len(dfa_states)):
            # Az adott állapotból kiinduló átmenetek, élcímke szerint
            for symbol in out_alphabet:
                key = (idx, symbol)
                if key in dfa_transitions:
                    target_idx = dfa_transitions[key]
                    out_transitions.append(
                        f"s{idx} {symbol} s{target_idx}"
                    )

        # ---------- Fájlba írás ----------
        with open(args.output, 'w') as f:
            f.write(" ".join(state_names) + "\n")
            f.write(" ".join(out_alphabet) + "\n")
            f.write(out_start + "\n")
            f.write(" ".join(out_accept) + "\n")
            for t in out_transitions:
                f.write(t + "\n")