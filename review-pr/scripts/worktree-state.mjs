import { execFile } from "node:child_process";
import { readFile, rename, writeFile } from "node:fs/promises";
import { randomUUID } from "node:crypto";
import { promisify } from "node:util";

const exec = promisify(execFile);

export async function run(command, args, cwd) {
  const { stdout } = await exec(command, args, {
    cwd,
    maxBuffer: 64 * 1024 * 1024,
    env: { ...process.env, GIT_TERMINAL_PROMPT: "0" },
  });
  return stdout;
}

export async function git(cwd, ...args) {
  return (await run("git", args, cwd)).trimEnd();
}

export async function readJson(file) {
  return JSON.parse(await readFile(file, "utf8"));
}

export async function saveRecord(file, record) {
  const temporary = `${file}.${randomUUID()}.tmp`;
  await writeFile(temporary, `${JSON.stringify(record, null, 2)}\n`, {
    mode: 0o600,
  });
  await rename(temporary, file);
}

// Match ordinary GitHub HTTPS and SSH remotes without persisting credentials.
export function githubRepo(remote) {
  const match =
    /^(?:https:\/\/(?:[^/@]+@)?github\.com\/|ssh:\/\/git@github\.com\/|git@github\.com:)([^/\s]+\/[^/\s]+?)\/?$/.exec(
      remote,
    );
  return match?.[1].replace(/\.git$/, "").toLowerCase();
}

export async function verifyRemote(root, remote, repo) {
  const url = await git(root, "remote", "get-url", remote);
  if (githubRepo(url) !== repo.toLowerCase()) {
    throw new Error(`Remote ${remote} does not point to github.com/${repo}.`);
  }
}

export async function fetchRefs(record, refspecs) {
  await verifyRemote(record.repository, record.remote, record.pr.repo);
  await git(
    record.repository,
    "fetch",
    "--atomic",
    "--no-tags",
    "--no-recurse-submodules",
    "--no-write-fetch-head",
    "--refmap=",
    record.remote,
    ...refspecs,
  );
}

export function detail(error) {
  // execFile's message embeds its complete argv. Prefer Git's diagnostic.
  return error.stderr?.trim() || error.message;
}
