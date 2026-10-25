"""Bundled adapters and explicitly selected, trusted adapter modules."""
import importlib.util
from pathlib import Path
import re
import sys

from .claude import ClaudeAdapter
from .codex import CodexAdapter


def production_adapters(specifications=()):
    adapters = {'claude': ClaudeAdapter(), 'codex': CodexAdapter()}
    for specification in specifications:
        name, separator, filename = specification.partition('=')
        if not separator or not re.fullmatch(r'[a-zA-Z0-9_-]+', name) or not filename:
            raise ValueError('Adapter registration must be NAME=/path/to/adapter.py')
        if name in adapters:
            raise ValueError(f'Adapter already registered: {name}')
        path = Path(filename).resolve()
        if not path.is_file() or path.suffix != '.py':
            raise ValueError(f'Adapter must be an existing Python module: {path}')
        module_name = '_panel_adapter_' + name
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ValueError(f'Cannot load adapter module: {path}')
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
            factory = getattr(module, 'create_adapter', None)
            if not callable(factory):
                raise ValueError('Module must export create_adapter()')
            adapter = factory()
            missing = [method for method in ('start', 'resume', 'cancel') if not callable(getattr(adapter, method, None))]
            if missing:
                raise ValueError('Adapter is missing: ' + ', '.join(missing))
        except Exception as exc:
            sys.modules.pop(module_name, None)
            raise ValueError(f'Cannot register adapter {name}: {exc}') from exc
        adapters[name] = adapter
    return adapters
