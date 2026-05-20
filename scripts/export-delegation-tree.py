#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
FIXTURE_PATH = ROOT / "benchmarks" / "exporter-fixtures" / "sample-composer-data.json"
PROJECT_ROOT_MARKERS = (
    ".git",
    "README.md",
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "composer.json",
)


@dataclass
class ComposerNode:
    composer_id: str
    name: str
    subtitle: str
    unified_mode: str
    force_mode: str
    created_at: int | None
    last_updated_at: int | None
    context_usage_percent: float | None
    lines_added: int
    lines_removed: int
    files_changed: int
    is_archived: bool
    is_draft: bool
    is_worktree: bool
    num_subcomposers: int
    active_branch: str | None
    branches: list[str]
    parent_composer_id: str | None
    subagent_type_name: str | None
    parent_request_id: str | None
    root_parent_request_id: str | None
    tool_call_id: str | None
    raw: dict[str, Any] = field(repr=False)


@dataclass
class WorkspaceSnapshot:
    source: str
    workspace_id: str
    db_path: Path | None
    project_path: str | None
    remote_url: str | None
    composers: list[ComposerNode]


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def read_json_file(path: Path) -> Any:
    for encoding in ("utf-8", "utf-8-sig"):
        try:
            return json.loads(path.read_text(encoding=encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise ValueError(f"Could not parse JSON file {path}")


def detect_workspace_storage() -> Path:
    home = Path.home()
    candidates = [
        home / "Library/Application Support/Cursor/User/workspaceStorage",
        home / ".config/Cursor/User/workspaceStorage",
        home / "AppData/Roaming/Cursor/User/workspaceStorage",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def decode_sqlite_value(value: Any) -> str:
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", "ignore")
    return str(value)


def decode_file_uri_path(uri_object: Any) -> str | None:
    if not isinstance(uri_object, dict):
        return None
    path_value = uri_object.get("path")
    if isinstance(path_value, str) and path_value:
        return unquote(path_value)
    external = uri_object.get("external")
    if isinstance(external, str) and external.startswith("file://"):
        return unquote(external[7:])
    return None


def path_from_raw_value(value: str) -> Path | None:
    if not value:
        return None
    decoded = unquote(value)
    if decoded.startswith("file:///"):
        decoded = decoded[7:]
    if os.name == "nt" and decoded.startswith("/") and len(decoded) > 3 and decoded[2] == ":":
        decoded = decoded[1:]
    path = Path(decoded)
    if path.suffix:
        return path.parent
    return path


def promote_to_project_root(path: Path) -> Path:
    current = path.resolve()
    best = current
    while True:
        if any((current / marker).exists() for marker in PROJECT_ROOT_MARKERS):
            best = current
        if current.parent == current:
            break
        current = current.parent
    return best


def common_project_path(candidates: list[Path]) -> str | None:
    if not candidates:
        return None
    normalized = [promote_to_project_root(path) for path in candidates]
    try:
        common = Path(os.path.commonpath([str(path) for path in normalized]))
    except ValueError:
        return None
    return str(promote_to_project_root(common))


def infer_project_path_from_editor_state(connection: sqlite3.Connection) -> str | None:
    inferred_paths: list[Path] = []
    fallback_keys = [
        "history.entries",
        "memento/workbench.editors.files.textFileEditor",
        "memento/workbench.parts.editor",
    ]
    for key in fallback_keys:
        row = connection.execute("SELECT value FROM ItemTable WHERE key=?", (key,)).fetchone()
        if not row:
            continue
        text = decode_sqlite_value(row[0])
        for match in re.findall(r"file:///[^\"'\s]+", text):
            path = path_from_raw_value(match)
            if path:
                inferred_paths.append(path)
        for match in re.findall(r"/Users/[^\"'\s]+|[A-Za-z]:\\\\[^\"'\s]+", text):
            path = path_from_raw_value(match)
            if path:
                inferred_paths.append(path)
    return common_project_path(inferred_paths)


def timestamp_to_iso(value: int | None) -> str | None:
    if not value:
        return None
    return (
        datetime.fromtimestamp(value / 1000, tz=timezone.utc)
        .astimezone()
        .isoformat(timespec="seconds")
    )


def load_composers_from_data(data: Any) -> list[ComposerNode]:
    if not isinstance(data, dict):
        raise ValueError("composer data must be a JSON object")
    all_composers = data.get("allComposers")
    if not isinstance(all_composers, list):
        raise ValueError('composer data must contain "allComposers" list')

    composers: list[ComposerNode] = []
    for item in all_composers:
        if not isinstance(item, dict):
            continue
        subagent = item.get("subagentInfo") or {}
        active_branch = item.get("activeBranch") or {}
        branches = []
        for branch in item.get("branches") or []:
            if isinstance(branch, dict):
                name = branch.get("branchName")
                if isinstance(name, str) and name:
                    branches.append(name)
        composers.append(
            ComposerNode(
                composer_id=str(item.get("composerId") or ""),
                name=str(item.get("name") or ""),
                subtitle=str(item.get("subtitle") or ""),
                unified_mode=str(item.get("unifiedMode") or ""),
                force_mode=str(item.get("forceMode") or ""),
                created_at=item.get("createdAt"),
                last_updated_at=item.get("lastUpdatedAt") or item.get("createdAt"),
                context_usage_percent=(
                    float(item["contextUsagePercent"])
                    if item.get("contextUsagePercent") is not None
                    else None
                ),
                lines_added=int(item.get("totalLinesAdded") or 0),
                lines_removed=int(item.get("totalLinesRemoved") or 0),
                files_changed=int(item.get("filesChangedCount") or 0),
                is_archived=bool(item.get("isArchived")),
                is_draft=bool(item.get("isDraft")),
                is_worktree=bool(item.get("isWorktree")),
                num_subcomposers=int(item.get("numSubComposers") or 0),
                active_branch=active_branch.get("branchName")
                if isinstance(active_branch, dict)
                else None,
                branches=branches,
                parent_composer_id=subagent.get("parentComposerId")
                if isinstance(subagent, dict)
                else None,
                subagent_type_name=subagent.get("subagentTypeName")
                if isinstance(subagent, dict)
                else None,
                parent_request_id=subagent.get("parentRequestId")
                if isinstance(subagent, dict)
                else None,
                root_parent_request_id=subagent.get("rootParentRequestId")
                if isinstance(subagent, dict)
                else None,
                tool_call_id=subagent.get("toolCallId") if isinstance(subagent, dict) else None,
                raw=item,
            )
        )
    return composers


def load_workspace_from_db(db_path: Path) -> WorkspaceSnapshot | None:
    try:
        connection = sqlite3.connect(str(db_path))
    except sqlite3.Error:
        return None

    try:
        composer_row = connection.execute(
            "SELECT value FROM ItemTable WHERE key='composer.composerData'"
        ).fetchone()
        if not composer_row:
            return None
        composer_data = json.loads(decode_sqlite_value(composer_row[0]))
        composers = load_composers_from_data(composer_data)

        workspace_row = connection.execute(
            "SELECT value FROM ItemTable WHERE key='workbench.backgroundComposer.workspacePersistentData'"
        ).fetchone()
        project_path = None
        remote_url = None
        if workspace_row:
            workspace_data = json.loads(decode_sqlite_value(workspace_row[0]))
            selected_remote = workspace_data.get("cachedSelectedRemote") or {}
            project_path = decode_file_uri_path(selected_remote.get("rootUri"))
            remote_url = (
                selected_remote.get("url")
                if isinstance(selected_remote.get("url"), str)
                else None
            )
        if not project_path:
            project_path = infer_project_path_from_editor_state(connection)

        return WorkspaceSnapshot(
            source="state.vscdb",
            workspace_id=db_path.parent.name,
            db_path=db_path,
            project_path=project_path,
            remote_url=remote_url,
            composers=composers,
        )
    finally:
        connection.close()


def load_workspace_from_composer_file(path: Path) -> WorkspaceSnapshot:
    data = read_json_file(path)
    composers = load_composers_from_data(data)
    return WorkspaceSnapshot(
        source="composer-data",
        workspace_id=path.stem,
        db_path=None,
        project_path=None,
        remote_url=None,
        composers=composers,
    )


def list_workspace_snapshots(workspace_storage: Path) -> list[WorkspaceSnapshot]:
    snapshots: list[WorkspaceSnapshot] = []
    if not workspace_storage.exists():
        return snapshots
    for child in sorted(workspace_storage.iterdir()):
        db_path = child / "state.vscdb"
        if not db_path.exists():
            continue
        snapshot = load_workspace_from_db(db_path)
        if snapshot:
            snapshots.append(snapshot)
    return snapshots


def path_matches(candidate: str | None, requested: Path) -> bool:
    if not candidate:
        return False
    try:
        candidate_path = Path(candidate).resolve()
        requested_path = requested.resolve()
    except OSError:
        return False

    if candidate_path == requested_path:
        return True
    try:
        requested_path.relative_to(candidate_path)
        return True
    except ValueError:
        pass
    try:
        candidate_path.relative_to(requested_path)
        return True
    except ValueError:
        return False


def choose_snapshot(
    snapshots: list[WorkspaceSnapshot],
    workspace_id: str | None,
    project_path: str | None,
) -> WorkspaceSnapshot:
    if not snapshots:
        raise ValueError("No Cursor workspaces with composer.composerData were found")

    if workspace_id:
        for snapshot in snapshots:
            if snapshot.workspace_id == workspace_id:
                return snapshot
        raise ValueError(f'Workspace id "{workspace_id}" was not found')

    requested_path = Path(project_path).resolve() if project_path else Path.cwd().resolve()
    path_matches_found = [s for s in snapshots if path_matches(s.project_path, requested_path)]
    if path_matches_found:
        return max(path_matches_found, key=snapshot_last_updated)

    return max(snapshots, key=snapshot_last_updated)


def snapshot_last_updated(snapshot: WorkspaceSnapshot) -> int:
    timestamps = [node.last_updated_at or 0 for node in snapshot.composers]
    return max(timestamps, default=0)


def redact_path(path: str | None, show_paths: bool) -> str | None:
    if not path:
        return None
    if show_paths:
        return path
    candidate = Path(path)
    return candidate.name or "(hidden)"


def filter_nodes(
    snapshot: WorkspaceSnapshot,
    include_archived: bool,
    include_chat: bool,
) -> list[ComposerNode]:
    filtered = []
    for node in snapshot.composers:
        if not include_archived and node.is_archived:
            continue
        if not include_chat and node.unified_mode and node.unified_mode != "agent":
            continue
        filtered.append(node)
    return filtered


def build_children_map(nodes: list[ComposerNode]) -> dict[str, list[ComposerNode]]:
    children: dict[str, list[ComposerNode]] = defaultdict(list)
    node_ids = {node.composer_id for node in nodes}
    for node in nodes:
        parent = node.parent_composer_id
        if parent and parent in node_ids:
            children[parent].append(node)
    for siblings in children.values():
        siblings.sort(key=lambda item: item.last_updated_at or 0, reverse=True)
    return children


def select_roots(
    nodes: list[ComposerNode],
    root_composer_id: str | None,
    all_roots: bool,
) -> list[ComposerNode]:
    nodes_by_id = {node.composer_id: node for node in nodes}
    if root_composer_id:
        if root_composer_id not in nodes_by_id:
            raise ValueError(f'Composer id "{root_composer_id}" not found in selected dataset')
        return [nodes_by_id[root_composer_id]]

    roots = [
        node
        for node in nodes
        if not node.parent_composer_id or node.parent_composer_id not in nodes_by_id
    ]
    roots.sort(key=lambda item: item.last_updated_at or 0, reverse=True)
    if all_roots:
        return roots
    return roots[:1]


def flatten_subtree(root: ComposerNode, children: dict[str, list[ComposerNode]]) -> list[ComposerNode]:
    ordered: list[ComposerNode] = []

    def visit(node: ComposerNode) -> None:
        ordered.append(node)
        for child in children.get(node.composer_id, []):
            visit(child)

    visit(root)
    return ordered


def summarize(snapshot: WorkspaceSnapshot, roots: list[ComposerNode], children: dict[str, list[ComposerNode]]) -> dict[str, Any]:
    selected_nodes: list[ComposerNode] = []
    for root in roots:
        selected_nodes.extend(flatten_subtree(root, children))

    agent_counts = Counter(
        node.subagent_type_name or "root" for node in selected_nodes
    )
    max_depth = 0

    def depth(node: ComposerNode, current: int) -> None:
        nonlocal max_depth
        max_depth = max(max_depth, current)
        for child in children.get(node.composer_id, []):
            depth(child, current + 1)

    for root in roots:
        depth(root, 0)

    return {
        "workspaceId": snapshot.workspace_id,
        "source": snapshot.source,
        "projectPath": snapshot.project_path,
        "remoteUrl": snapshot.remote_url,
        "selectedRoots": len(roots),
        "selectedComposers": len(selected_nodes),
        "maxDepth": max_depth,
        "agentCounts": dict(sorted(agent_counts.items())),
        "latestUpdatedAt": timestamp_to_iso(snapshot_last_updated(snapshot)),
    }


def node_to_dict(
    node: ComposerNode,
    children: dict[str, list[ComposerNode]],
    show_paths: bool,
) -> dict[str, Any]:
    return {
        "composerId": node.composer_id,
        "name": node.name,
        "subtitle": node.subtitle,
        "agent": node.subagent_type_name or "root",
        "parentComposerId": node.parent_composer_id,
        "requestIds": {
            "parentRequestId": node.parent_request_id,
            "rootParentRequestId": node.root_parent_request_id,
        },
        "toolCallId": " ".join(node.tool_call_id.split()) if node.tool_call_id else None,
        "unifiedMode": node.unified_mode,
        "forceMode": node.force_mode,
        "createdAt": timestamp_to_iso(node.created_at),
        "lastUpdatedAt": timestamp_to_iso(node.last_updated_at),
        "contextUsagePercent": node.context_usage_percent,
        "changes": {
            "linesAdded": node.lines_added,
            "linesRemoved": node.lines_removed,
            "filesChanged": node.files_changed,
        },
        "activeBranch": node.active_branch,
        "branches": node.branches,
        "isArchived": node.is_archived,
        "isDraft": node.is_draft,
        "isWorktree": node.is_worktree,
        "numSubcomposers": node.num_subcomposers,
        "children": [
            node_to_dict(child, children, show_paths) for child in children.get(node.composer_id, [])
        ],
    }


def render_text(
    snapshot: WorkspaceSnapshot,
    roots: list[ComposerNode],
    children: dict[str, list[ComposerNode]],
    show_paths: bool,
) -> str:
    summary = summarize(snapshot, roots, children)
    lines = [
        f"Workspace: {summary['workspaceId']}",
        f"Source: {summary['source']}",
    ]
    project_label = redact_path(snapshot.project_path, show_paths)
    if project_label:
        suffix = "" if show_paths else " (hidden path; use --show-paths)"
        lines.append(f"Project: {project_label}{suffix}")
    if snapshot.remote_url:
        lines.append(f"Remote: {snapshot.remote_url}")
    lines.append(f"Selected roots: {summary['selectedRoots']}")
    lines.append(f"Selected composers: {summary['selectedComposers']}")
    lines.append(f"Max depth: {summary['maxDepth']}")
    agent_counts = ", ".join(
        f"{name}={count}" for name, count in summary["agentCounts"].items()
    )
    lines.append(f"Agent counts: {agent_counts or '(none)'}")
    lines.append("")
    lines.append("Delegation tree:")

    def walk(node: ComposerNode, prefix: str) -> None:
        label = node.name or "(unnamed)"
        agent = node.subagent_type_name or "root"
        updated = timestamp_to_iso(node.last_updated_at) or "unknown"
        changes = f"+{node.lines_added}/-{node.lines_removed}, {node.files_changed} files"
        context = (
            f"{node.context_usage_percent:.1f}%"
            if node.context_usage_percent is not None
            else "n/a"
        )
        lines.append(
            f"{prefix}- {label} [{agent}] id={node.composer_id} updated={updated} ctx={context} changes={changes}"
        )
        if node.subtitle:
            lines.append(f"{prefix}  subtitle: {node.subtitle}")
        if node.active_branch or node.branches:
            branch_text = ", ".join(node.branches or ([node.active_branch] if node.active_branch else []))
            lines.append(f"{prefix}  branches: {branch_text}")
        if node.parent_request_id or node.root_parent_request_id:
            lines.append(
                f"{prefix}  requestIds: parent={node.parent_request_id or '-'} root={node.root_parent_request_id or '-'}"
            )
        for child in children.get(node.composer_id, []):
            walk(child, prefix + "  ")

    for root in roots:
        walk(root, "")

    return "\n".join(lines)


def render_markdown(
    snapshot: WorkspaceSnapshot,
    roots: list[ComposerNode],
    children: dict[str, list[ComposerNode]],
    show_paths: bool,
) -> str:
    summary = summarize(snapshot, roots, children)
    project_label = redact_path(snapshot.project_path, show_paths)
    lines = [
        "# Delegation Tree",
        "",
        f"- Workspace: `{summary['workspaceId']}`",
        f"- Source: `{summary['source']}`",
    ]
    if project_label:
        suffix = "" if show_paths else " (hidden path; use `--show-paths`)"
        lines.append(f"- Project: `{project_label}`{suffix}")
    if snapshot.remote_url:
        lines.append(f"- Remote: `{snapshot.remote_url}`")
    lines.append(f"- Selected roots: `{summary['selectedRoots']}`")
    lines.append(f"- Selected composers: `{summary['selectedComposers']}`")
    lines.append(f"- Max depth: `{summary['maxDepth']}`")
    lines.append("")
    lines.append("## Trees")
    lines.append("")

    def walk(node: ComposerNode, depth: int) -> None:
        indent = "  " * depth
        agent = node.subagent_type_name or "root"
        line = f"{indent}- `{agent}` `{node.composer_id}` {node.name or '(unnamed)'}"
        lines.append(line)
        meta = []
        if node.subtitle:
            meta.append(f"subtitle={node.subtitle}")
        if node.context_usage_percent is not None:
            meta.append(f"ctx={node.context_usage_percent:.1f}%")
        meta.append(f"files={node.files_changed}")
        if node.branches:
            meta.append(f"branches={','.join(node.branches)}")
        lines.append(f"{indent}  {', '.join(meta)}")
        for child in children.get(node.composer_id, []):
            walk(child, depth + 1)

    for root in roots:
        walk(root, 0)

    return "\n".join(lines)


def render_json(
    snapshot: WorkspaceSnapshot,
    roots: list[ComposerNode],
    children: dict[str, list[ComposerNode]],
    show_paths: bool,
) -> str:
    summary = summarize(snapshot, roots, children)
    payload = {
        "workspace": {
            "workspaceId": snapshot.workspace_id,
            "source": snapshot.source,
            "projectPath": snapshot.project_path if show_paths else None,
            "projectLabel": redact_path(snapshot.project_path, show_paths),
            "remoteUrl": snapshot.remote_url,
            "dbPath": str(snapshot.db_path) if snapshot.db_path and show_paths else None,
        },
        "summary": summary,
        "roots": [node_to_dict(root, children, show_paths) for root in roots],
    }
    if not show_paths:
        payload["summary"]["projectPath"] = None
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_workspace_list(snapshots: list[WorkspaceSnapshot], show_paths: bool) -> str:
    lines = ["Available Cursor workspaces:"]
    for snapshot in sorted(snapshots, key=snapshot_last_updated, reverse=True):
        project_label = redact_path(snapshot.project_path, show_paths) or "(unknown)"
        suffix = "" if show_paths else " (hidden path)"
        agent_count = sum(1 for node in snapshot.composers if node.unified_mode == "agent")
        latest = timestamp_to_iso(snapshot_last_updated(snapshot)) or "unknown"
        lines.append(
            f"- {snapshot.workspace_id} | project={project_label}{suffix} | composers={len(snapshot.composers)} | agent={agent_count} | latest={latest}"
        )
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Safely export Cursor/Codex delegation trees from state.vscdb or composer data JSON."
    )
    parser.add_argument("--workspace-storage", help="Path to Cursor workspaceStorage directory")
    parser.add_argument("--workspace-id", help="Select a specific workspaceStorage directory id")
    parser.add_argument("--project-path", help="Prefer the workspace whose project path matches this path")
    parser.add_argument("--db", help="Path to a specific state.vscdb file")
    parser.add_argument("--composer-data", help="Path to exported composer.composerData JSON")
    parser.add_argument("--root-composer-id", help="Limit output to a specific root/subtree composer id")
    parser.add_argument("--all-roots", action="store_true", help="Emit every detected root tree")
    parser.add_argument("--include-archived", action="store_true", help="Include archived composers")
    parser.add_argument("--include-chat", action="store_true", help="Include non-agent/chat composers")
    parser.add_argument("--list-workspaces", action="store_true", help="List available workspaces and exit")
    parser.add_argument(
        "--format",
        choices=("text", "markdown", "json"),
        default="text",
        help="Output format",
    )
    parser.add_argument("--show-paths", action="store_true", help="Show absolute local paths in output")
    parser.add_argument("--output", help="Write output to a file instead of stdout")
    return parser.parse_args(argv)


def write_output(text: str, output_path: str | None) -> None:
    if output_path:
        Path(output_path).write_text(text + ("\n" if not text.endswith("\n") else ""), encoding="utf-8")
        return
    print(text)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    if args.composer_data:
        snapshot = load_workspace_from_composer_file(Path(args.composer_data).resolve())
        snapshots = [snapshot]
    elif args.db:
        snapshot = load_workspace_from_db(Path(args.db).resolve())
        if not snapshot:
            return fail(f'Could not load composer data from "{args.db}"')
        snapshots = [snapshot]
    else:
        workspace_storage = (
            Path(args.workspace_storage).expanduser().resolve()
            if args.workspace_storage
            else detect_workspace_storage()
        )
        snapshots = list_workspace_snapshots(workspace_storage)
        if args.list_workspaces:
            if not snapshots:
                return fail(f"No workspaces found under {workspace_storage}")
            write_output(render_workspace_list(snapshots, args.show_paths), args.output)
            return 0
        snapshot = choose_snapshot(snapshots, args.workspace_id, args.project_path)

    nodes = filter_nodes(
        snapshot,
        include_archived=args.include_archived,
        include_chat=args.include_chat,
    )
    if not nodes:
        return fail("No composers remain after filtering")

    children = build_children_map(nodes)
    roots = select_roots(nodes, args.root_composer_id, args.all_roots)
    if not roots:
        return fail("No root composers were found")

    if args.format == "json":
        text = render_json(snapshot, roots, children, args.show_paths)
    elif args.format == "markdown":
        text = render_markdown(snapshot, roots, children, args.show_paths)
    else:
        text = render_text(snapshot, roots, children, args.show_paths)

    write_output(text, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
