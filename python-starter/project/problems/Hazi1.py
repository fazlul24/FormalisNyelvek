from project.problem import Problem


class DFAProblem(Problem):

    def initialize_parser(self, parser):
        # A --check kapcsoló regisztrálása
        parser.add_argument(
            '--check',
            help='vesszővel elválasztott szó(k), pl. a,ab,abc'
        )

    def is_chosen_problem(self, args):
        # Ez a probléma akkor fut, ha a --check meg van adva
        return args.check is not None

    def run(self, args):
        # --- Bemeneti fájl beolvasása ---
        with open(args.input, 'r') as f:
            lines = [line.strip() for line in f if line.strip() != '']

        # 1. sor: állapotok
        states = lines[0].split()
        # 2. sor: ábécé
        alphabet = lines[1].split()
        # 3. sor: kezdőállapot
        start_state = lines[2]
        # 4. sor: végállapotok
        accept_states = set(lines[3].split())
        # további sorok: átmenetek:  from symbol to
        transitions = {}
        for line in lines[4:]:
            parts = line.split()
            if len(parts) != 3:
                continue
            from_state, symbol, to_state = parts
            transitions.setdefault(from_state, {})[symbol] = to_state

        # --- Elfogadás vizsgálata ---
        def accepts(word: str) -> bool:
            current = start_state
            for ch in word:
                if current in transitions and ch in transitions[current]:
                    current = transitions[current][ch]
                else:
                    return False  # nincs ilyen átmenet → elutasítva
            return current in accept_states

        # --- Szavak feldolgozása ---
        words = args.check.split(',')

        # --- Eredmények kiírása ---
        with open(args.output, 'w') as f:
            for word in words:
                f.write("IGEN\n" if accepts(word) else "NEM\n")