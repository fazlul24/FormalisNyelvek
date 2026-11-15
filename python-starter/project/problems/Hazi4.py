from project.problem import Problem
import re


class RegexProblem(Problem):

    # Logcat sorok általános mintája (a feladatban megadott segítség alapján)
    # 1: dátum+idő, 2: PID, 3: TID, 4: szint, 5: tag, 6: message
    LOG_RE = re.compile(
        r'([0-9-]+ [0-9:.]+) +([0-9]+) +([0-9]+) +([IDVEFAW]) +(.+?):(.*)'
    )

    def initialize_parser(self, parser):
        parser.add_argument(
            '--rgx',
            type=int,
            help='regex task number (1-5)'
        )

    def is_chosen_problem(self, args):
        return getattr(args, 'rgx', None) is not None

    def run(self, args):
        with open(args.input, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        task = args.rgx
        if task == 1:
            results = self._task1(content)
        elif task == 2:
            results = self._task2(content)
        elif task == 3:
            results = self._task3(content)
        elif task == 4:
            results = self._task4(content)
        elif task == 5:
            results = self._task5(content)
        else:
            raise ValueError(f"Unknown regex task: {task}")

        with open(args.output, 'w') as f:
            for line in results:
                f.write(str(line) + "\n")

    def _task1(self, content):
        patterns = [
            # a) 10. hónap 15-én kelt sorok
            r'^10-15 +[0-9:.]+ +[0-9]+ +[0-9]+ +[IDVEFAW] +.+?:',
            # b) 10-15 10:18:51-kor kelt sorok
            r'^10-15 +10:18:51[0-9.]* +[0-9]+ +[0-9]+ +[IDVEFAW] +.+?:',
            # c) 51. másodpercben kelt sorok (bármely perc)
            r'^[0-9-]+ +[0-9]{2}:[0-9]{2}:51[0-9.]* +[0-9]+ +[0-9]+ +[IDVEFAW] +.+?:',
            # d) lowmemorykiller taget tartalmazó sorok
            r'^[0-9-]+ +[0-9:.]+ +[0-9]+ +[0-9]+ +[IDVEFAW] +lowmemorykiller:',
            # e) 10:18:51-kor kelt, 221-es PID-ű sorok
            r'^[0-9-]+ +10:18:51[0-9.]* +221 +[0-9]+ +[IDVEFAW] +.+?:',
            # f) E (error) sorok
            r'^[0-9-]+ +[0-9:.]+ +[0-9]+ +[0-9]+ +E +.+?:',
            # g) PackageManager által küldött W (warning) sorok
            r'^[0-9-]+ +[0-9:.]+ +[0-9]+ +[0-9]+ +W +PackageManager:',
            # h) ExoPlayer-es D (debug) sorok
            r'^[0-9-]+ +[0-9:.]+ +[0-9]+ +[0-9]+ +D +ExoPlayer[^:]*:',
            # i) E vagy W sorok, amelyek message-ében .java: pozíció van
            r'^[0-9-]+ +[0-9:.]+ +[0-9]+ +[0-9]+ +[EW] +[^:]+:[^\n]*\.java:',
            # j) Thread szó a message-ben (nem a tagben)
            r'^[0-9-]+ +[0-9:.]+ +[0-9]+ +[0-9]+ +[IDVEFAW] +[^:]+:[^\n]*Thread',
        ]
        return [len(re.findall(p, content, re.MULTILINE)) for p in patterns]

    def _task2(self, content):
        results = []
        for m in self.LOG_RE.finditer(content):
            if m.group(4) != 'E':
                continue
            message = m.group(6) or ''
            for fm in re.finditer(r'[\w$]+\.java', message):
                results.append(fm.group(0))
        return results

    def _task3(self, content):
        results = []
        seen = set()
        for m in self.LOG_RE.finditer(content):
            pid = m.group(2)
            if pid not in seen:
                seen.add(pid)
                results.append(pid)
        return results

    def _task4(self, content):
        counts = {}
        order = []
        for m in self.LOG_RE.finditer(content):
            if m.group(4) == 'E':
                pid = m.group(2)
                if pid not in counts:
                    counts[pid] = 0
                    order.append(pid)
                counts[pid] += 1
        if not counts:
            return []
        max_count = max(counts.values())
        for pid in order:
            if counts[pid] == max_count:
                return [f"PID={pid} ({max_count} errors)"]

    def _task5(self, content):
        count = 0
        for m in self.LOG_RE.finditer(content):
            if m.group(4) == 'E' and m.group(2) == m.group(3):
                count += 1
        return [count]