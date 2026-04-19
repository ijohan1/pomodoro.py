import os, json, time, threading, sys
from datetime import datetime

floppy = ("""
BBBBBBBBBBBBBBBBBBBBBBBBBBB
BMB---------------------B B
BBB---------------------BBB
BBB---------------------BBB
BBB---------------------BBB
BBB---------------------BBB
BBB---------------------BBB
BBBBBBBBBBBBBBBBBBBBBBBBBBB
BBBBB++++++++++++++++BBBBBB
BBBBB++BBBBB+++++++++BBBBBB
BBBBB++BBBBB+++++++++BBBBBB
BBBBB++BBBBB+++++++++BBBBBB
BBBBB++++++++++++++++BBBBBB """)

cacti = ("""
      ,`""',
      ;' ` ;
      ;`,',;
      ;' ` ;
 ,,,  ;`,',;
;,` ; ;' ` ;   ,',
;`,'; ;`,',;  ;,' ;
;',`; ;` ' ; ;`'`';
;` '',''` `,',`',;
 `''`'; ', ;`'`'
      ;' `';
      ;` ' ;
      ;' `';
      ;` ' ;
      ; ',';
      ;,' ';
      -------- """ )
#-----робочі інтервали--------
work = 25 * 60
breakk = 10 * 60
lunch = 15 * 60
#_____________________________
waiting = False
running = True
def clear(): os.system('cls' if os.name=='nt' else 'clear')

paused = False
state = "work"
worked = 0
sessions = 0
totalseconds = 0

def ascii(state):
    if state == "work":
        return floppy
    else: return cacti


def beep():
    if sys.platform.startswith("win"):
        import winsound
        winsound.Beep(1000, 3000)
    else:
        os.system('canberra-gtk-play -i complete')


def render(paused, state, seconds, sessions):
    clear()
    print(ascii(state))
    mins, secs = divmod(seconds, 60)
    line = (f" | {state} |  {mins:02d}:{secs:02d} | "f"пропрацьовано сесій: {sessions} |")
    if paused:
        print(line + " ⏸ ") #, end = "\r"
    else: print(line) #, end = "\r"

def basetimer(duration, state, sessions):
    global paused, waiting, totalseconds, running
    start = time.time()
    elapsed = 0
    lastpaused = None
    seconds = duration
#=======пауза і рух===========
    while seconds > 0 and running:
        if paused:
            if lastpaused is None: lastpaused = time.time()
            render(paused, state, seconds, sessions)
            time.sleep(0.1)
            continue

        if lastpaused is not None:
            elapsed += time.time() - lastpaused
            lastpaused = None

        elapsed_ = int(time.time() - start - elapsed)
        seconds = duration - elapsed_

        render(paused, state, seconds, sessions)
        time.sleep(0.2)
#=======================
    global totalseconds
    totalseconds += duration
    beep()
    print("час вийшов. далі? (enter)")
    waiting = True
    while waiting and running: time.sleep(0.1)

def worktimer(sessions):
    basetimer(work, "work", sessions)

def breaktimer(sessions):
    basetimer(breakk, "break", sessions)

def lunchtimer(sessions):
    basetimer(lunch, "lunch", sessions)

def inputs():
    global paused, waiting, running, sessions
    while True:
        cmd = input()
        if cmd == "q":
            running = waiting = False
            break

        if waiting: waiting =  False
        else:
            paused = not paused
            if not paused: clear()


def showstats():
    clear()
    hours = totalseconds // 3600
    mins = (totalseconds % 3600) // 60
    secs = totalseconds % 60
    print(f"роботу завершено.\n відроблених помодоро сесій: {sessions}.\n було відпрацьовано {hours}г. {mins}хв. {secs}с.")


def main():
    global state, sessions
    counter = 0

    while running:
        if state == "work":
            worktimer(sessions)
            counter += 1
            sessions += 1
            if counter %4 == 0: state = "lunch"
            else: state = "break"

        elif state == "break":
            breaktimer(sessions)
            state = "work"

        elif state == "lunch":
            lunchtimer(sessions)
            state = "work"


def writing():
    global totalseconds, sessions
    if totalseconds <= 0: return
    today = datetime.now().strftime("%d/%m/%y")

    base = os.path.dirname(os.path.abspath(__file__))
    datdir = os.path.join(base, "data")
    os.makedirs(datdir, exist_ok = True)

    file = os.path.join(datdir, "statistics.json")
    if os.path.exists(file):
        with open(file, "r") as f:
            data = json.load(f)
    else: data = {}


    entry = {
        "sessions": sessions,
        "time": f"{totalseconds//3600}h {(totalseconds%3600)//60}m {totalseconds%60}s",
        "time_seconds": totalseconds
        }

    if today not in data:
        data[today] = []
    data[today].append(entry)
    with open(file, "w") as f: json.dump(data, f, indent=4)

if __name__ == "__main__":
    print("\033[?25l")
    t = threading.Thread(target=inputs, daemon=True)
    t.start()
    try: main()
    finally:
        writing()
        showstats()
