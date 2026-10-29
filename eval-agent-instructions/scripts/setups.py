"""Setups: a harness, a model, a reasoning effort and, for OpenRouter models, the upstream providers.

configs.json holds what each harness needs (`harnesses`: its environment, any
settings for its own config file, and the instruction file it reads), what each known model
needs (`models`, keyed by short name), and the presets runs name often
(`presets`). A setup is written as a spec, `{"harness", "model", "effort",
"provider"}`, or as the name of a preset. A model missing from `models` is
given by its full id, such as `openrouter/vendor/model`.

A setup's name is `<harness>-<model>-<effort>`, ending in the first provider for
OpenRouter models; its config is what the runner and the stored-baseline check
read, so equal specs always resolve to equal configs.
"""

# OpenClaw needs a context window; a model the catalog lacks gets a common one.
DEFAULT_CONTEXT_WINDOW = 131072


def resolve(spec: dict, settings: dict) -> tuple[str, dict]:
    """The setup's name and config."""
    harness = spec["harness"]
    if harness not in settings["harnesses"]:
        raise SystemExit(f"unknown harness {harness}; choose from {sorted(settings['harnesses'])}")
    short = spec["model"]
    model = settings["models"].get(short)
    if model is None:
        if "/" not in short:
            raise SystemExit(f"unknown model {short}; name one from configs.json or give its full id")
        model, short = {"id": short}, short.rsplit("/", 1)[1]
    effort = spec.get("effort") or "high"
    effort = None if effort == "default" else effort
    config = {"harness": harness, "model": model["id"], "effort": effort}
    for key in ("env", "native_config", "workspace_setup", "max_sessions"):
        if key in settings["harnesses"][harness]:
            config[key] = settings["harnesses"][harness][key]
    name = f"{harness}-{short}-{effort or 'default'}"
    if model["id"].startswith("openrouter/"):
        providers = provider_order(spec.get("provider"), model.get("providers", []))
        if providers:
            config["openrouter_providers"] = providers
            name += f"-{providers[0]}"
        if "max_tokens" in model:
            config["max_tokens"] = model["max_tokens"]
        if harness == "openclaw":
            config["context_window"] = model.get("context_window", DEFAULT_CONTEXT_WINDOW)
    elif spec.get("provider"):
        raise SystemExit(f"--provider applies to OpenRouter models only, not {model['id']}")
    return name, config


def provider_order(provider: str | None, preferred: list[str]) -> list[str]:
    """Providers to try in order: the given ones first, then the model's other preferred ones.

    A comma-separated list is taken as the whole order; one provider the model does
    not prefer, such as a first-party endpoint, is tried alone.
    """
    if not provider:
        return list(preferred)
    if "," in provider:
        return provider.split(",")
    if provider not in preferred:
        return [provider]
    return [provider] + [p for p in preferred if p != provider]


def catalog(settings: dict) -> dict[str, dict]:
    """Every preset by name."""
    configs = {}
    for spec in settings["presets"]:
        name, config = resolve(spec, settings)
        if name in configs:
            raise SystemExit(f"configs.json lists preset {name} twice")
        configs[name] = config
    return configs
