# Section 2: Basics

## 2.2.1 Docker ensures reproducibility

**Problem 1 (`docker-setup`)**

1. Paste the commands you used to pull `ubuntu:22.04` and start an interactive container, followed by the output from inside the container that confirms its operating system (e.g., `cat /etc/os-release`).

   ```text
   $ docker pull ubuntu:22.04
   22.04: Pulling from library/ubuntu
   f74d428f3a50: Pull complete
   f1ed2c25af57: Download complete
   Digest: sha256:f64b2ffc2f10ab8f8505aa56b2664bd846cbb9df87c7e2532e30f7667021c0e6
   Status: Downloaded newer image for ubuntu:22.04
   docker.io/library/ubuntu:22.04

   $ docker run -it ubuntu:22.04 bash
   root@01c452b21379:/# cat /etc/os-release
   PRETTY_NAME="Ubuntu 22.04.5 LTS"
   NAME="Ubuntu"
   VERSION_ID="22.04"
   VERSION="22.04.5 LTS (Jammy Jellyfish)"
   VERSION_CODENAME=jammy
   ID=ubuntu
   ID_LIKE=debian
   HOME_URL="https://www.ubuntu.com/"
   SUPPORT_URL="https://help.ubuntu.com/"
   BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
   PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
   UBUNTU_CODENAME=jammy
   root@01c452b21379:/# exit
   exit
   ```

## 2.2.2 Harbor defines evaluation primitives

**Problem 2 (`harbor-setup`)**

1. Paste the output of `uv run harbor --version` and `docker version`.

   ```text
   $ uv run harbor --version
   0.18.0

   $ docker version
   Client:
   Version:           29.9.3
   API version:       1.56
   Go version:        go1.26.10
   Git commit:        5457199
   Built:             Tue Nov  3 21:41:57 2026
   OS/Arch:           darwin/arm64
   Context:           desktop-linux

   Server: Docker Desktop 4.99.0 (245822)
   Engine:
   Version:          29.9.3
   API version:      1.56 (minimum version 1.40)
   Go version:       go1.26.10
   Git commit:       70efc0e
   Built:            Tue Nov  3 21:41:25 2026
   OS/Arch:          linux/arm64
   Experimental:     false
   containerd:
   Version:          v2.4.2
   GitCommit:        b7a25261e029d68978bbf290df0a62fc819b3c51
   runc:
   Version:          1.5.2
   GitCommit:        v1.5.2-0-g29dd3dc2
   docker-init:
   Version:          0.19.0
   GitCommit:        de40ad0
   ```

2. From `uv run harbor --help`, which commands start an evaluation job and browse completed results?

   ```text
   $ uv run harbor --help

   Usage: harbor [OPTIONS] COMMAND [ARGS]...

   ╭─ Options ──────────────────────────────────────────────────────────────────╮
   │ --version             -v                                                   │
   │ --install-completion            Install completion for the current shell.  │
   │ --show-completion               Show completion for the current shell, to  │
   │                                 copy it or customize the installation.     │
   │ --help                -h        Show this message and exit.                │
   ╰────────────────────────────────────────────────────────────────────────────╯
   ╭─ Commands ─────────────────────────────────────────────────────────────────╮
   │ check        Check task quality against a rubric.                          │
   │ analyze      Analyze trial trajectories.                                   │
   │ init         Initialize a new task or dataset.                             │
   │ run          Start a job. Alias for `harbor job start`.                    │
   │ exec         Compile paths into tasks and run a job.                       │
   │ publish      Publish tasks and datasets to the Harbor registry.            │
   │ upload       Upload job results to the Harbor platform.                    │
   │ add          Add tasks or datasets to a dataset.toml.                      │
   │ download     Download a task or dataset.                                   │
   │ remove       Remove tasks from a dataset.toml.                             │
   │ sync         Update task digests in a dataset manifest.                    │
   │ view         Start web server to browse trajectory files.                  │
   │ adapter      Manage adapters.                                              │
   │ task         Manage tasks.                                                 │
   │ dataset      Manage datasets.                                              │
   │ job          Manage jobs.                                                  │
   │ hub          View Harbor Hub jobs, tasks, and trials.                      │
   │ trial        Manage trials.                                                │
   │ cache        Manage Harbor cache.                                          │
   │ plugins      Manage job plugins.                                           │
   │ auth         Manage authentication.                                        │
   │ leaderboard  Manage leaderboards.                                          │
   ╰────────────────────────────────────────────────────────────────────────────╯


   `harbor run` starts an evaluation job and `harbor view` browses completed results by starting a web server over the trajectory files.
   ```