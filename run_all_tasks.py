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
    # Patch the dialog to return our values and patch expInfo before the dialog is shown
    orig_gui_DlgFromDict = getattr(PVT_Script.gui, 'DlgFromDict', None)
    orig_core_quit = getattr(PVT_Script.core, 'quit', None)
    class DummyDlg:
        def __init__(self, expInfo, title=None):
            expInfo['Participant ID'] = participant_id
            expInfo['Treatment'] = treatment
            self.data = [participant_id, treatment]
            self.OK = True
        def show(self):
            return True
    PVT_Script.gui.DlgFromDict = DummyDlg
    # Patch expInfo in the module if it exists
    setattr(PVT_Script, 'expInfo', {'Participant ID': participant_id, 'Treatment': treatment})
    # Patch core.quit in the module to prevent exit
    def dummy_core_quit():
        pass
    PVT_Script.core.quit = dummy_core_quit
    # Patch os.path.join to intercept filename creation
    import os as _os
    orig_os_path_join = _os.path.join
    def patched_join(*args):
        # If this is the filename creation, inject participant_id and treatment
        if len(args) >= 2 and args[0] == 'PVT Data' and args[1].endswith('_PVT_' + args[1].split('_PVT_')[-1]):
            timestamp = args[1].split('_PVT_')[-1]
            if treatment:
                return orig_os_path_join('PVT Data', f'{participant_id}_{treatment}_PVT_{timestamp}')
            else:
                return orig_os_path_join('PVT Data', f'{participant_id}_PVT_{timestamp}')
        return orig_os_path_join(*args)
    _os.path.join = patched_join
    try:
        PVT_Script.run_pvt_study()
    finally:
        if orig_gui_DlgFromDict:
            PVT_Script.gui.DlgFromDict = orig_gui_DlgFromDict
        if orig_core_quit:
            PVT_Script.core.quit = orig_core_quit
        _os.path.join = orig_os_path_join

run_pvt_with_args(participant_id, treatment)

# --- Trailmaking ---
def run_trailmaking_with_args(participant_id, treatment):
    # Patch the dialog to return our values and patch expInfo before the dialog is shown
    orig_gui_DlgFromDict = getattr(V4_Trailmaking_Script.gui, 'DlgFromDict', None)
    orig_core_quit = getattr(V4_Trailmaking_Script.core, 'quit', None)
    class DummyDlg:
        def __init__(self, expInfo, title=None):
            expInfo['Participant ID'] = participant_id
            expInfo['Treatment'] = treatment
            self.data = [participant_id, treatment]
            self.OK = True
        def show(self):
            return True
    V4_Trailmaking_Script.gui.DlgFromDict = DummyDlg
    setattr(V4_Trailmaking_Script, 'expInfo', {'Participant ID': participant_id, 'Treatment': treatment})
    def dummy_core_quit():
        pass
    V4_Trailmaking_Script.core.quit = dummy_core_quit
    import os as _os
    orig_os_path_join = _os.path.join
    def patched_join(*args):
        # If this is the filename creation, inject participant_id and treatment
        if len(args) >= 2 and args[0] == 'Trailmaking Data' and args[1].endswith('_TMT_Master.csv'):
            if treatment:
                return orig_os_path_join('Trailmaking Data', f'{participant_id}_{treatment}_TMT_Master.csv')
            else:
                return orig_os_path_join('Trailmaking Data', f'{participant_id}_TMT_Master.csv')
        return orig_os_path_join(*args)
    _os.path.join = patched_join
    try:
        V4_Trailmaking_Script.run_experiment()
    finally:
        if orig_gui_DlgFromDict:
            V4_Trailmaking_Script.gui.DlgFromDict = orig_gui_DlgFromDict
        if orig_core_quit:
            V4_Trailmaking_Script.core.quit = orig_core_quit
        _os.path.join = orig_os_path_join

run_trailmaking_with_args(participant_id, treatment)