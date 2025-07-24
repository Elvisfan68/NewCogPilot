

from psychopy import visual, core, event
import random
import csv
import datetime
import os

# === Helper Functions ===

def get_text_input(win, prompt, allowed_chars, max_len=20):
    input_text = ''
    prompt_stim = visual.TextStim(win, text=prompt, color='black', height=0.05, pos=(0, 0.2))
    text_stim = visual.TextStim(win, text='', color='black', height=0.05, pos=(0, 0))
    instructions = visual.TextStim(win, text="Press ENTER to confirm, BACKSPACE to delete.",
                                   pos=(0, -0.2), color='gray', height=0.035)

    while True:
        prompt_stim.draw()
        text_stim.text = input_text
        text_stim.draw()
        instructions.draw()
        win.flip()

        keys = event.waitKeys()
        for key in keys:
            if key == 'return':
                return input_text.strip()
            elif key == 'backspace':
                input_text = input_text[:-1]
            elif key.lower() in allowed_chars and len(input_text) < max_len:
                input_text += key

def wait_for_key():
    event.waitKeys()

# === Setup ===

win = visual.Window(fullscr=True, color='white', units='height')

# Collect participant info
name = get_text_input(win, "Enter your name:", allowed_chars=list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ "))
group = get_text_input(win, "Enter group (1, 2, or 3):", allowed_chars=['1', '2', '3'])

participant_name = name.replace(" ", "_") or "anonymous"
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
results_dir = "stroop_data"
os.makedirs(results_dir, exist_ok=True)
filename = os.path.join(results_dir, f"stroop_results_{participant_name}_G{group}_{timestamp}.csv")

# Define visual components (now using height units)
text_stim = visual.TextStim(win=win, text='', height=0.15, pos=(0, 0))
instruction = visual.TextStim(win=win, text='', color='black', height=0.05, wrapWidth=1.5)
feedback = visual.TextStim(win=win, text='', color='black', height=0.05)
end_message = visual.TextStim(win=win, text='', color='black', height=0.05)

# === Familiarization ===

instruction.text = (
    "FAMILIARIZATION TEST\n\n"
    "You will now answer some questions to ensure you understand the task.\n\n"
    "Remember: Press R for RED, G for GREEN, B for BLUE (based on the INK COLOR).\n\n"
    "Press any key to start."
)
instruction.draw()
win.flip()
wait_for_key()

# Familiarization trials (word, ink color, correct key)
familiarization_trials = [
    ("RED", "green", "g"),
    ("GREEN", "red", "r"),
    ("BLUE", "blue", "b"),
    ("GREEN", "blue", "b"),
    ("RED", "red", "r")
]

color_rgb_map = {'red': [1, -1, -1], 'green': [-1, 1, -1], 'blue': [-1, -1, 1]}
key_map = {'r': 'red', 'g': 'green', 'b': 'blue'}
key_label = {'r': 'R', 'g': 'G', 'b': 'B'}

for word, color_name, correct_key in familiarization_trials:
    question = (
        f"If the word \"{word}\" appears in {color_name.upper()} ink,\n"
        f"what key should you press?"
    )
    instruction.text = question + "\n\nPress R for RED, G for GREEN, B for BLUE."
    instruction.draw()
    win.flip()

    keys = event.waitKeys(keyList=['r', 'g', 'b'])
    response = keys[0].lower()

    if response == correct_key:
        feedback.text = "Correct!"
    else:
        correct_color = color_name.upper()
        feedback.text = (
            f"Wrong!\nThe correct answer is '{key_label[correct_key]}' because the ink is {correct_color},\n"
            f"even though the word says \"{word}\"."
        )
    feedback.draw()
    win.flip()
    core.wait(2)

instruction.text = "Great! You're ready to start the real task.\n\nPress any key to begin."
instruction.draw()
win.flip()
wait_for_key()

# === Color Stroop Task ===

instruction.text = (
    "STROOP TASK STARTING\n\n"
    "Press R for RED, G for GREEN, B for BLUE (based on ink color).\n\n"
    "Press ESC to quit at any time.\n\nPress any key to start."
)
instruction.draw()
win.flip()
wait_for_key()

words = ['RED', 'BLUE', 'GREEN']
results = []

for trial in range(60):  # Main task
    word = random.choice(words)
    color_name = random.choice(list(color_rgb_map.keys()))
    color_rgb = color_rgb_map[color_name]

    text_stim.text = word
    text_stim.color = color_rgb
    text_stim.pos = (0, 0)
    text_stim.draw()
    win.flip()

    start_time = core.getTime()
    keys = event.waitKeys(keyList=['r', 'g', 'b', 'escape'])
    rt = core.getTime() - start_time

    if 'escape' in keys:
        win.close()
        core.quit()

    response = key_map.get(keys[0].lower(), '')
    correct = (response == color_name)

    results.append([
        trial + 1, word, color_name, response, correct,
        round(rt * 1000), participant_name, group, timestamp
    ])

    feedback.text = "Correct!" if correct else "Wrong!"
    feedback.draw()
    win.flip()
    core.wait(0.5)

# === End Message ===

end_message.text = "Done! You completed the task.\nPress any key to exit."
end_message.draw()
win.flip()
wait_for_key()
win.close()

# === Save Results ===

with open(filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        'Trial', 'Word', 'Color_Shown', 'Response', 'Correct',
        'Reaction_Time_ms', 'Participant', 'Group', 'Timestamp'
    ])
    writer.writerows(results)

    correct_trials = sum(1 for r in results if r[4])
    accuracy = (correct_trials / len(results)) * 100 if results else 0
    avg_rt = sum(r[5] for r in results if r[4]) / correct_trials if correct_trials > 0 else 0

    writer.writerow([])
    writer.writerow(['Summary'])
    writer.writerow(['Percent Accuracy (%)', f"{accuracy:.2f}"])
    writer.writerow(['Average RT (ms) Correct Answers', f"{avg_rt:.0f}"])


