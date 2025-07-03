from psychopy import gui, core
import sys
import inspect
import types

# Set a global flag so the tasks know they're being run in sequence
RUNNING_ALL_TASKS = True

# Patch core.quit and sys.exit to only close the window, not the process
def patched_core_quit():
    # Just close all windows, but don't exit the process
    for win in core.openWindows:
        try:
            win.close()
        except Exception:
            pass
    # Do not call sys.exit()

def patched_sys_exit(*args, **kwargs):
    # Do nothing
    pass

core.quit = patched_core_quit
sys.exit = patched_sys_exit

# 1. Ask for participant info once
expInfo = {'Participant ID': '', 'Treatment': ''}
dlg = gui.DlgFromDict(expInfo, title='Study')
if not dlg.OK:
    import sys; sys.exit()

participant_id = expInfo['Participant ID']
treatment = expInfo['Treatment']

# 2. Import and run each task, passing participant info
import ABart_Top_Off_Color_v2
import PVT_Script
import V4_Trailmaking_Script

# --- BART ---
if hasattr(ABart_Top_Off_Color_v2, 'run_bart'):
    ABart_Top_Off_Color_v2.run_bart(participant_id, treatment)
else:
    # Monkeypatch: override dialog in BART
    orig_get_participant_info = getattr(ABart_Top_Off_Color_v2.BART, 'get_participant_info', None)
    def patched_get_participant_info(self):
        self.participant_id = participant_id
        self.treatment = treatment
    ABart_Top_Off_Color_v2.BART.get_participant_info = patched_get_participant_info
    bart = ABart_Top_Off_Color_v2.BART()
    bart.run()
    if orig_get_participant_info:
        ABart_Top_Off_Color_v2.BART.get_participant_info = orig_get_participant_info

# --- PVT ---
def run_pvt_with_args(participant_id, treatment):
    # Try to call with arguments if possible, else patch the dialog
    sig = inspect.signature(PVT_Script.run_pvt_study)
    if len(sig.parameters) >= 2:
        return PVT_Script.run_pvt_study(participant_id, treatment)
    else:
        # Patch the dialog to return our values
        orig_gui_DlgFromDict = getattr(PVT_Script.gui, 'DlgFromDict', None)
        class DummyDlg:
            def __init__(self, expInfo, title=None):
                expInfo['Participant ID'] = participant_id
                expInfo['Treatment'] = treatment
                self.data = [participant_id, treatment]
                self.OK = True
            def show(self):
                return True
        PVT_Script.gui.DlgFromDict = DummyDlg
        try:
            PVT_Script.run_pvt_study()
        finally:
            if orig_gui_DlgFromDict:
                PVT_Script.gui.DlgFromDict = orig_gui_DlgFromDict

run_pvt_with_args(participant_id, treatment)

# --- Trailmaking ---
def run_trailmaking_with_args(participant_id, treatment):
    sig = inspect.signature(V4_Trailmaking_Script.run_experiment)
    param_names = list(sig.parameters.keys())
    if 'participant_id' in param_names and 'treatment' in param_names:
        return V4_Trailmaking_Script.run_experiment(participant_id, treatment)
    else:
        # Patch the dialog to return our values
        orig_gui_DlgFromDict = getattr(V4_Trailmaking_Script.gui, 'DlgFromDict', None)
        class DummyDlg:
            def __init__(self, expInfo, title=None):
                expInfo['Participant ID'] = participant_id
                expInfo['Treatment'] = treatment
                self.data = [participant_id, treatment]
                self.OK = True
            def show(self):
                return True
        V4_Trailmaking_Script.gui.DlgFromDict = DummyDlg
        try:
            V4_Trailmaking_Script.run_experiment()
        finally:
            if orig_gui_DlgFromDict:
                V4_Trailmaking_Script.gui.DlgFromDict = orig_gui_DlgFromDict

run_trailmaking_with_args(participant_id, treatment)