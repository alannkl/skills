"""Executable checks use the same bounded process lifecycle as harness invocations."""
from adapters.base import ProcessAdapter, Terminal


class CheckAdapter(ProcessAdapter):
    def command(self, session_id, settings):
        return settings['argv'], 'runner-check'

    def parse(self, output, code, session_id):
        return Terminal(session_id, raw_text=output, block={'exit_status': code},
                        exit_status=code, outcome='completed' if code == 0 else 'failed',
                        error='' if code == 0 else 'Executable check failed')
