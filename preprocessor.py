import re


class Preprocessor:
    def __init__(self, source):
        self.source = source if source else ""
        self.macros = {}
        self.includes = []

    def preprocess(self):
        if not self.source.strip():
            return self.source

        lines = self.source.splitlines()
        processed_lines = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith('#define'):
                match = re.match(r'#define\s+(\w+)\s+(.*)', stripped)
                if match:
                    name, value = match.groups()
                    self.macros[name] = value.strip()
                continue

            if stripped.startswith('#include'):
                match = re.match(r'#include\s*[<"](.+)[>"]', stripped)
                if match:
                    self.includes.append(match.group(1))
                continue

            for name, value in self.macros.items():
                try:
                    line = re.sub(r'\b' + re.escape(name) + r'\b', value, line)
                except re.error:
                    pass

            processed_lines.append(line)

        return "\n".join(processed_lines)

    def get_report(self):
        report = []
        report.append(f"\n{'='*55}")
        report.append(f"{'PHASE 0: PREPROCESSING':^55}")
        report.append(f"{'='*55}")
        report.append(f"Includes found: {', '.join(self.includes) if self.includes else 'None'}")
        report.append(f"Macros defined: {', '.join([f'{k}={v}' for k,v in self.macros.items()]) if self.macros else 'None'}")
        report.append(f"{'='*55}\n")
        return "\n".join(report)

    def print_report(self):
        print(self.get_report())


if __name__ == '__main__':
    code = """
#include <stdio.h>
#define PI 3.14
#define MAX(a,b) ((a)>(b)?(a):(b))

int main() {
    float r = 10.0;
    float area = PI * r * r;
    return 0;
}
"""
    pp = Preprocessor(code)
    result = pp.preprocess()
    pp.print_report()
    print("Processed Code:")
    print(result)
