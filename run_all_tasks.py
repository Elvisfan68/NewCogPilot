from psychopy import gui, core
import sys

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
if hasattr(PVT_Script, 'run_pvt_study') and PVT_Script.run_pvt_study.__code__.co_argcount >= 2:
    PVT_Script.run_pvt_study(participant_id, treatment)
else:
    # Monkeypatch: override dialog in PVT
    orig_run_pvt_study = getattr(PVT_Script, 'run_pvt_study', None)
    def patched_run_pvt_study():
        return orig_run_pvt_study(participant_id=participant_id, treatment=treatment)
    if orig_run_pvt_study:
        import types
        PVT_Script.run_pvt_study = types.FunctionType(
            orig_run_pvt_study.__code__,
            orig_run_pvt_study.__globals__,
            name=orig_run_pvt_study.__name__,
            argdefs=orig_run_pvt_study.__defaults__,
            closure=orig_run_pvt_study.__closure__
        )
        PVT_Script.run_pvt_study = lambda: orig_run_pvt_study(participant_id=participant_id, treatment=treatment)
        PVT_Script.run_pvt_study()

# --- Trailmaking ---
if hasattr(V4_Trailmaking_Script, 'run_experiment') and V4_Trailmaking_Script.run_experiment.__code__.co_argcount >= 2:
    V4_Trailmaking_Script.run_experiment(participant_id, treatment)
else:
    # Monkeypatch: override dialog in Trailmaking
    orig_run_experiment = getattr(V4_Trailmaking_Script, 'run_experiment', None)
    def patched_run_experiment():
        return orig_run_experiment(participant_id=participant_id, treatment=treatment)
    if orig_run_experiment:
        import types
        V4_Trailmaking_Script.run_experiment = types.FunctionType(
            orig_run_experiment.__code__,
            orig_run_experiment.__globals__,
            name=orig_run_experiment.__name__,
            argdefs=orig_run_experiment.__defaults__,
            closure=orig_run_experiment.__closure__
        )
        V4_Trailmaking_Script.run_experiment = lambda: orig_run_experiment(participant_id=participant_id, treatment=treatment)
        V4_Trailmaking_Script.run_experiment()