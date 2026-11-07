#!/usr/bin/env python3
"""Exercise the real shared QML service without accessing the desktop session."""
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time

with tempfile.TemporaryDirectory(prefix="buds-shared-state-") as directory:
    test_dir = Path(__file__).resolve().parent
    plugin_dir = test_dir.parent.as_uri()
    Path(directory, "shell.qml").write_text((test_dir / "qml/shell.qml").read_text())
    consumer = (test_dir / "qml/Consumer.qml").read_text()
    consumer = consumer.replace('"../.."', '"' + plugin_dir + '"')
    Path(directory, "Consumer.qml").write_text(consumer)
    env = dict(os.environ, QT_QPA_PLATFORMTHEME="", QT_QPA_PLATFORM="offscreen",
               QT_QUICK_BACKEND="software", XDG_RUNTIME_DIR=directory,
               XDG_CACHE_HOME=directory + "/cache", XDG_STATE_HOME=directory + "/state",
               DBUS_SESSION_BUS_ADDRESS="unix:path=" + directory + "/no-session-bus")
    env.pop("WAYLAND_DISPLAY", None)
    with open(directory + "/output", "w+") as output:
        process = subprocess.Popen(
            ["quickshell", "-p", directory + "/shell.qml"],
            env=env, stdout=output, stderr=output, start_new_session=True)
        try:
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                output.seek(0)
                log = output.read()
                if "PASS: Buds service" in log:
                    print("shared-state.py: all checks passed")
                    break
                if process.poll() is not None:
                    raise RuntimeError(log)
                time.sleep(0.05)
            else:
                raise RuntimeError("QML test timed out:\n" + log)
        finally:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            process.wait(timeout=5)
