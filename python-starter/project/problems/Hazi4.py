import re
from collections import Counter

from project.problem import Problem

# Egy logsor eleje: dátum, idő, pid, tid
PREFIX = r'^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ '

# A feladatban megadott kifejezés (2-5. feladathoz)
# 1: teljes, 2: időbélyeg, 3: pid, 4: tid, 5: szint, 6: tag, 7: üzenet
LOG_RE = re.compile(
    r'(([0-9-]+ [0-9:.]+) +([0-9]+) +([0-9]+) ([IDVEFAW]) (.+?):(?: (.+))?)'
)

# 1. feladat: minden alpont egy reguláris kifejezés
TASK1_PATTERNS = [re.compile(p) for p in (
    # 1. 10. hónap 15-én létrejött sorok
    r'^10-15 ',
    # 2. 10-15 10:18:51-kor létrejött sorok
    r'^10-15 10:18:51\.',
    # 3. 51 másodperckor létrejött sorok (bármilyen perc/óra)
    r'^[0-9-]+ [0-9]{2}:[0-9]{2}:51\.',
    # 4. lowmemorykiller tag
    PREFIX + r'[IDVEFAW] lowmemorykiller *:',
    # 5. 10:18:51-kor keletkezett, 221-es pid
    r'^[0-9-]+ 10:18:51\.[0-9]+ +221 +[0-9]+ ',
    # 6. hibák (E)
    PREFIX + r'E ',
    # 7. PackageManager warningok
    PREFIX + r'W PackageManager *:',
    # 8. ExoPlayer debug sorok
    PREFIX + r'D ExoPlayer[^:]*:',
    # 9. E vagy W sorok, amelyek .java: pozíciót tartalmaznak
    PREFIX + r'[EW] .*\.java:',
    # 10. "Thread" szó a message részben (a tag az első kettőspontig tart)
    PREFIX + r'[IDVEFAW] [^:]+: .*Thread',
)]

# 2. feladat: java állomány neve a stack trace-ből
JAVA_FILE_RE = re.compile(r'([\w$]+\.java):[0-9]+')

# 5. feladat: főszál hiba (pid == tid) visszahivatkozással
MAIN_THREAD_ERROR_RE = re.compile(r'^[0-9-]+ [0-9:.]+ +([0-9]+) +\1 E ')


class RegexProblem(Problem):

    def initialize_parser(self, parser):
        parser.add_argument('--rgx', type=int, choices=range(1, 6),
                            help='regex feladat sorszáma (1-5)')

    def is_chosen_problem(self, args):
        return args.rgx is not None

    def run(self, args):
        solvers = {
            1: self.task1,
            2: self.task2,
            3: self.task3,
            4: self.task4,
            5: self.task5,
        }

        with open(args.input, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        results = solvers[args.rgx](lines)

        with open(args.output, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(f'{result}\n')

    # ------------------------------------------------------------------
    @staticmethod
    def parse(lines):
        """Visszaadja az összes sor illesztését a megadott kifejezésre."""
        for line in lines:
            match = LOG_RE.match(line)
            if match:
                yield match

    def task1(self, lines):
        return [
            sum(1 for line in lines if pattern.search(line))
            for pattern in TASK1_PATTERNS
        ]

    def task2(self, lines):
        files = []
        for m in self.parse(lines):
            if m.group(5) == 'E':
                files.extend(JAVA_FILE_RE.findall(m.group(0)))
        return files

    def task3(self, lines):
        # a dict megőrzi a beszúrási sorrendet, így az első előfordulás szerint rendez
        return list(dict.fromkeys(m.group(3) for m in self.parse(lines)))

    def task4(self, lines):
        errors = Counter(m.group(3) for m in self.parse(lines)
                         if m.group(5) == 'E')
        if not errors:
            return []
        # döntetlennél az először megjelenő pid nyer
        pid, count = errors.most_common(1)[0]
        return [f'PID={pid} ({count} errors)']

    def task5(self, lines):
        return [sum(1 for line in lines if MAIN_THREAD_ERROR_RE.match(line))]