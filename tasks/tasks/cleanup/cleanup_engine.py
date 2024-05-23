from tasks.configs.constants import CLEANUP_MACROS as MACROS
from tasks.tasks.cleanup.line_validation import (
    line_validation_for_select_only,
    line_validation_for_select_not,
    line_validation_for_checkpoints,
)
from tasks.tasks.foundation.macro_engine import MacroEngine


class CleanupEngine(MacroEngine):

    def validate_select_only_macro(self, line):
        if result := line_validation_for_select_only(line):
            return (MACROS.SELECT_ONLY, result)
        return None

    def validate_select_not_macro(self, line):
        if result := line_validation_for_select_not(line):
            return (MACROS.SELECT_NOT, result)
        return None

    def validate_checkpoints_macro(self, line):
        if line_validation_for_checkpoints(line):
            return (MACROS.CHECKPOINTING, True)
        return None

    def post_process_macros(self, macros_data):
        select_not = []
        select_only = []
        checkpoint_tag = False
        for macro, content in macros_data:
            if macro == MACROS.SELECT_NOT:
                select_not.extend(content)
            elif macro == MACROS.SELECT_ONLY:
                select_only.extend(content)
            elif macro == MACROS.CHECKPOINTING:
                checkpoint_tag = True

        select_not = list(set(select_not)) or None
        select_only = list(set(select_only)) or None
        return select_only, select_not, checkpoint_tag
