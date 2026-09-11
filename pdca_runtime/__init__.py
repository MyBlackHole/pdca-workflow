"""Platform-neutral runtime for one PDCA task and one fresh execution agent."""

from .errors import RuntimeContractError
from .lifecycle import (
    bind_agent,
    build_context_manifest,
    derive_execution_state,
    prepare_dispatch_request,
    record_conformance_decision,
    record_agent_result,
    record_user_confirmation,
    resume_for_conformance,
)
from .projection import build_projection_manifest, verify_projection_manifest
from .task import ONTOLOGY_ROLES, ExecutableTask, load_executable_task

__all__ = [
    "ONTOLOGY_ROLES",
    "ExecutableTask",
    "RuntimeContractError",
    "bind_agent",
    "build_context_manifest",
    "build_projection_manifest",
    "derive_execution_state",
    "load_executable_task",
    "prepare_dispatch_request",
    "record_conformance_decision",
    "record_agent_result",
    "record_user_confirmation",
    "resume_for_conformance",
    "verify_projection_manifest",
]
