import sys
import tkinter as tk
import time
import math

HELP_TEXT = {
    "γενικά": """
Εντολές Κωνσταντίνας:

θέσε x = έκφραση
γράψε έκφραση

αν συνθήκη:
    ...
αλλιώς:
    ...
τέλος

όσο συνθήκη:
    ...
τέλος

συνάρτηση όνομα(παράμετροι):
    ...
    επέστρεψε τιμή
τέλος

GUI:
δημιούργησε_παράθυρο "Τίτλος"
δημιούργησε_καμβά όνομα πλάτος ύψος
γράψε_σε_ετικέτα "όνομα" "κείμενο"
αναλογικό_ρολόι
τρέξε
""",
    "παραδείγματα": """
Παράδειγμα Αναλογικού Ρολογιού:
-------------------------------
δημιούργησε_παράθυρο "Αναλογικό Ρολόι"
δημιούργησε_καμβά 400 400

αναλογικό_ρολόι

τρέξε
"""
}

class Interpreter:
    def __init__(self):
        self.vars = {}
        self.funcs = {}
        self.gui = {}

    def eval_expr(self, expr):
        return eval(expr, {"time": time, "math": math}, self.vars)

    def collect_block(self, lines, start):
        block = []
        depth = 0
        i = start
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith(("αν ", "όσο ", "συνάρτηση ")):
                depth += 1
            if line == "τέλος":
                if depth == 0:
                    return block, i
                depth -= 1
            block.append(lines[i])
            i += 1
        raise Exception("Λείπει 'τέλος'")

    def run(self, lines):
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith("#"):
                i += 1
                continue

            # GUI commands
            if line.startswith("δημιούργησε_παράθυρο"):
                title = line.split('"')[1]
                self.gui["root"] = tk.Tk()
                self.gui["root"].title(title)

            elif line.startswith("δημιούργησε_καμβά"):
                parts = line.split()
                name = "canvas"
                width = int(parts[1])
                height = int(parts[2])
                canvas = tk.Canvas(self.gui["root"], width=width, height=height, bg="white")
                canvas.pack()
                self.gui[name] = canvas
                self.gui["canvas_w"] = width
                self.gui["canvas_h"] = height

            elif line.startswith("γράψε_σε_ετικέτα"):
                name = line.split('"')[1]
                text = line.split('"')[3]
                self.gui[name].config(text=text)

            elif line == "αναλογικό_ρολόι":
                self.start_analog_clock()

            elif line == "τρέξε":
                self.gui["root"].mainloop()

            # standard commands
            elif line.startswith("γράψε"):
                print(self.eval_expr(line[6:].strip()))

            elif line.startswith("θέσε"):
                name, expr = line[5:].split("=", 1)
                self.vars[name.strip()] = self.eval_expr(expr.strip())

            elif line.startswith("αν"):
                condition = line[2:].strip()[:-1]
                block, end = self.collect_block(lines, i + 1)
                else_block = []
                if "αλλιώς:" in [l.strip() for l in block]:
                    idx = [l.strip() for l in block].index("αλλιώς:")
                    else_block = block[idx + 1:]
                    block = block[:idx]
                if self.eval_expr(condition):
                    self.run(block)
                else:
                    self.run(else_block)
                i = end

            elif line.startswith("όσο"):
                condition = line[4:].strip()[:-1]
                block, end = self.collect_block(lines, i + 1)
                if "root" in self.gui:
                    self.run_loop_gui(block, condition)
                else:
                    while self.eval_expr(condition):
                        self.run(block)
                i = end

            elif line.startswith("συνάρτηση"):
                name, args = line[10:].split("(")
                args = args.replace("):", "").split(",")
                block, end = self.collect_block(lines, i + 1)
                self.funcs[name.strip()] = (args, block)
                self.vars[name.strip()] = lambda *a, n=name.strip(): self.call_func(n, *a)
                i = end

            elif line.startswith("επέστρεψε"):
                return self.eval_expr(line[9:].strip())

            i += 1

    def call_func(self, name, *args):
        params, body = self.funcs[name]
        backup = self.vars.copy()
        for p, a in zip(params, args):
            self.vars[p.strip()] = a
        result = self.run(body)
        self.vars = backup
        return result

    def run_loop_gui(self, block, condition):
        def loop():
            if self.eval_expr(condition):
                self.run(block)
                self.gui["root"].after(1000, loop)
        loop()

    def start_analog_clock(self):
        canvas = self.gui["canvas"]
        w = self.gui["canvas_w"]
        h = self.gui["canvas_h"]
        cx, cy = w // 2, h // 2
        r = min(w, h) // 2 - 20

        def draw_clock():
            canvas.delete("all")

            # κύκλος
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r, width=4)

            # αριθμοί
            for n in range(1, 13):
                ang = math.radians(n * 30 - 90)
                x = cx + math.cos(ang) * (r - 30)
                y = cy + math.sin(ang) * (r - 30)
                canvas.create_text(x, y, text=str(n), font=("Arial", 14))

            # ώρα
            now = time.localtime()
            sec = now.tm_sec
            min_ = now.tm_min
            hr = now.tm_hour % 12

            # δείκτης δευτερολέπτων
            sec_ang = math.radians(sec * 6 - 90)
            sx = cx + math.cos(sec_ang) * (r - 20)
            sy = cy + math.sin(sec_ang) * (r - 20)
            canvas.create_line(cx, cy, sx, sy, fill="red", width=1)

            # δείκτης λεπτών
            min_ang = math.radians(min_ * 6 - 90)
            mx = cx + math.cos(min_ang) * (r - 40)
            my = cy + math.sin(min_ang) * (r - 40)
            canvas.create_line(cx, cy, mx, my, width=3)

            # δείκτης ωρών
            hr_ang = math.radians((hr * 30 + min_ * 0.5) - 90)
            hx = cx + math.cos(hr_ang) * (r - 70)
            hy = cy + math.sin(hr_ang) * (r - 70)
            canvas.create_line(cx, cy, hx, hy, width=5)

            canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="black")

            self.gui["root"].after(1000, draw_clock)

        draw_clock()


def repl():
    interpreter = Interpreter()
    print("Καλώς ήρθες στην Κωνσταντίνα")
    print("Πληκτρολόγησε 'βοήθεια' για οδηγίες ή 'έξοδος' για έξοδο.\n")

    while True:
        line = input("Κωνσταντίνα> ").strip()

        if line in ("έξοδος", "exit"):
            break

        if line.startswith(("βοήθεια", "help")):
            parts = line.split()
            key = parts[1] if len(parts) > 1 else "γενικά"
            print(HELP_TEXT.get(key, "Δεν υπάρχει βοήθεια για αυτό."))
            continue

        try:
            interpreter.run([line])
        except Exception as e:
            print("Σφάλμα:", e)


def run_file(filename):
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()
    interpreter = Interpreter()
    interpreter.run(lines)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        repl()



