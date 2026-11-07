import QtQuick
import Quickshell

ShellRoot {
  Consumer { id: first }
  Consumer { id: second }
  Component.onCompleted: {
    if (first.active || second.active) throw new Error("Fallback is active")
    first.clientProcessId = 123
    first.clientRunning = true
    first.applyText('{"schema_version":1,"process_id":123,"connected":true}')
    if (!first.connected) throw new Error("Connection did not propagate")
    first.applyText('{"schema_version":1,"process_id":123,"connected":false}')
    if (first.connected || first.supportsAnc)
      throw new Error("Disconnect did not disable controls")
    first.stateGone()
    if (first.statusFilePresent) throw new Error("Missing file did not propagate")
    console.log("PASS: Buds service connection, disconnect, and inactive fallback behavior")
  }
}
