

from psychopy import visual, core, event
import random
import csv
import datetime
import os

# === Helper Functions ===

def get_text_input(win, prompt, allowed_chars, max_len=20):
    input_text = ''
    prompt_stim = visual.TextStim(win, text=prompt, color='black', height=40, pos=(0, 100))
    text_stim = visual.TextStim(win, text='', color='black', height=40, pos=(0, 0))
    instructions = visual.TextStim(win, text="Press ENTER to confirm, BACKSPACE to delete.",
                                   pos=(0, -100), color='gray', height=30)

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

win = visual.Window(fullscr=True, color='white', units='pix')

# Collect participant info
name = get_text_input(win, "Enter your name:", allowed_chars=list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ "))
group = get_text_input(win, "Enter group (1, 2, or 3):", allowed_chars=['1', '2', '3'])

participant_name = name.replace(" ", "_") or "anonymous"
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
results_dir = "stroop_data"
os.makedirs(results_dir, exist_ok=True)
filename = os.path.join(results_dir, f"stroop_results_{participant_name}_G{group}_{timestamp}.csv")

# Define visual components
text_stim = visual.TextStim(win=win, text='', height=100, pos=(0, 0))
instruction = visual.TextStim(win=win, text="", color='black', height=40)
feedback = visual.TextStim(win=win, text='', color='black', height=40)
end_message = visual.TextStim(win=win, text='', color='black', height=40)

# === Part 1: Color Stroop ===

instruction.text = "Press R for RED, G for GREEN, B for BLUE.\n\nPress ESC to quit at any time.\n\nPress any key to start."
instruction.draw()
win.flip()
wait_for_key()

words = ['RED', 'BLUE', 'GREEN']
colors = {'red': [1, -1, -1], 'blue': [-1, -1, 1], 'green': [-1, 1, -1]}
key_map = {'r': 'red', 'g': 'green', 'b': 'blue'}

results = []

for trial in range(60):  # Doubled from 10
    word = random.choice(words)
    color_name = random.choice(list(colors.keys()))
    color_rgb = colors[color_name]

    text_stim.text = word
    text_stim.color = color_rgb
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

    results.append([trial + 1, word, color_name, response, correct, round(rt * 1000), participant_name, group, timestamp])

    feedback.text = "Correct!" if correct else "Wrong!"
    feedback.draw()
    win.flip()
    core.wait(0.5)

# End message for Part 1
end_message.text = "Done! Thank you.\nPress any key to continue to Part 2."
end_message.draw()
win.flip()
wait_for_key()

# Save Part 1 Results
with open(filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Trial', 'Word', 'Color_Shown', 'Response', 'Correct', 'Reaction_Time_ms', 'Participant', 'Group', 'Timestamp'])
    writer.writerows(results)

    correct_trials = sum(1 for r in results if r[4])
    accuracy = (correct_trials / len(results)) * 100 if results else 0
    avg_rt = sum(r[5] for r in results if r[4]) / correct_trials if correct_trials > 0 else 0

    writer.writerow([])
    writer.writerow(['Summary'])
    writer.writerow(['Percent Accuracy (%)', f"{accuracy:.2f}"])
    writer.writerow(['Average RT (ms) Correct Answers', f"{avg_rt:.0f}"])

# === Part 2: Spatial Stroop ===

instruction.text = (
    "PART 2: Spatial Stroop\n\nA word ('LEFT' or 'RIGHT') will appear on either the left or right side.\n\n"
    "Press 'T' if the word's meaning matches its position.\nPress 'F' if it does NOT match.\n\nPress any key to start."
)
instruction.draw()
win.flip()
wait_for_key()

spatial_results = []
positions = {'left': (-300, 0), 'right': (300, 0)}
spatial_words = ['LEFT', 'RIGHT']

for trial in range(60):  # Doubled from 10
    word = random.choice(spatial_words)
    pos_name = random.choice(['left', 'right'])
    pos = positions[pos_name]

    text_stim.text = word
    text_stim.color = 'black'
    text_stim.pos = pos
    text_stim.draw()
    win.flip()

    start_time = core.getTime()
    keys = event.waitKeys(keyList=['t', 'f', 'escape'])
    rt = core.getTime() - start_time

    if 'escape' in keys:
        win.close()
        core.quit()

    response = keys[0].lower()
    match = (word.lower() == pos_name)
    correct = (response == 't' and match) or (response == 'f' and not match)

    spatial_results.append([trial + 1, word, pos_name, response, correct, round(rt * 1000), participant_name, group, timestamp])

    feedback.text = "Correct!" if correct else "Wrong!"
    feedback.draw()
    win.flip()
    core.wait(0.5)

# End message for Part 2
end_message.text = "Done with Part 2! You completed all tasks.\nPress any key to exit."
end_message.draw()
win.flip()
wait_for_key()
win.close()

# Save Part 2 Results
with open(filename, 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([])
    writer.writerow(['=== Spatial Stroop Task Results ==='])
    writer.writerow(['Trial', 'Word', 'Position_Shown', 'Response', 'Correct', 'Reaction_Time_ms', 'Participant', 'Group', 'Timestamp'])
    writer.writerows(spatial_results)

    correct_trials = sum(1 for r in spatial_results if r[4])
    accuracy = (correct_trials / len(spatial_results)) * 100 if spatial_results else 0
    avg_rt = sum(r[5] for r in spatial_results if r[4]) / correct_trials if correct_trials > 0 else 0

    writer.writerow([])
    writer.writerow(['Summary'])
    writer.writerow(['Percent Accuracy (%)', f"{accuracy:.2f}"])
    writer.writerow(['Average RT (ms) Correct Answers', f"{avg_rt:.0f}"])

________________________________
From: Marco Pasquale Lombardo <marcol@stanford.edu>
Sent: Wednesday, July 23, 2025 2:28 PM
To: Colin Sang-Zen Liu <cszliu1@stanford.edu>
Subject: Re: longer code

that is all of it

________________________________
From: Marco Pasquale Lombardo
Sent: Wednesday, July 23, 2025 2:25 PM
To: Colin Sang-Zen Liu <cszliu1@stanford.edu>
Subject: longer code


    writer.writerow([])
    writer.writerow(['Summary'])
    writer.writerow(['Percent Accuracy (%)', f"{accuracy:.2f}"])
    writer.writerow(['Average RT (ms) Correct Answers', f"{avg_rt:.0f}"])

# === Part 2: Spatial Stroop ===

instruction.text = (
    "PART 2: Spatial Stroop\n\nA word ('LEFT' or 'RIGHT') will appear on either the left or right side.\n\n"
    "Press 'T' if the word's meaning matches its position.\nPress 'F' if it does NOT match.\n\nPress any key to start."
)
instruction.draw()
win.flip()
wait_for_key()

spatial_results = []
positions = {'left': (-300, 0), 'right': (300, 0)}
spatial_words = ['LEFT', 'RIGHT']

for trial in range(60):  # Doubled from 10
    word = random.choice(spatial_words)
    pos_name = random.choice(['left', 'right'])
    pos = positions[pos_name]

    text_stim.text = word
    text_stim.color = 'black'
    text_stim.pos = pos
    text_stim.draw()
    win.flip()

    start_time = core.getTime()
    keys = event.waitKeys(keyList=['t', 'f', 'escape'])
    rt = core.getTime() - start_time

    if 'escape' in keys:
        win.close()
        core.quit()

    response = keys[0].lower()
    match = (word.lower() == pos_name)
    correct = (response == 't' and match) or (response == 'f' and not match)

    spatial_results.append([trial + 1, word, pos_name, response, correct, round(rt * 1000), participant_name, group, timestamp])

    feedback.text = "Correct!" if correct else "Wrong!"
    feedback.draw()
    win.flip()
    core.wait(0.5)

# End message for Part 2
end_message.text = "Done with Part 2! You completed all tasks.\nPress any key to exit."
end_message.draw()
win.flip()
wait_for_key()
win.close()

# Save Part 2 Results
with open(filename, 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([])
    writer.writerow(['=== Spatial Stroop Task Results ==='])
    writer.writerow(['Trial', 'Word', 'Position_Shown', 'Response', 'Correct', 'Reaction_Time_ms', 'Participant', 'Group', 'Timestamp'])
    writer.writerows(spatial_results)

    correct_trials = sum(1 for r in spatial_results if r[4])
    accuracy = (correct_trials / len(spatial_results)) * 100 if spatial_results else 0
    avg_rt = sum(r[5] for r in spatial_results if r[4]) / correct_trials if correct_trials > 0 else 0

    writer.writerow([])
    writer.writerow(['Summary'])
    writer.writerow(['Percent Accuracy (%)', f"{accuracy:.2f}"])
    writer.writerow(['Average RT (ms) Correct Answers', f"{avg_rt:.0f}"])


