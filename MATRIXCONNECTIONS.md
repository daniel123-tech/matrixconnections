# MatrixConnections build notes

Rebranded build of [RustDesk](https://github.com/rustdesk/rustdesk) (AGPL-3.0) for a self-hosted
rustdesk-server (hbbs/hbbr). Source for this build is this repository plus the
`libs/hbb_common` submodule fork (daniel123-tech/hbb_common, branch `matrixconnections`).

## Where things are set
| What | File |
|---|---|
| App name (`APP_NAME`) | `libs/hbb_common/src/config.rs` |
| ID/rendezvous server (`RENDEZVOUS_SERVERS`) | `libs/hbb_common/src/config.rs` |
| Server public key (`RS_PUB_KEY`) | `libs/hbb_common/src/config.rs` |
| Windows exe version info | `flutter/windows/runner/Runner.rc`, `Cargo.toml`, `libs/portable/Cargo.toml` |
| Window title text | `flutter/lib/desktop/widgets/tabbar_widget.dart` |
| Build | `.github/workflows/matrixconnections-windows.yml` (run manually) |

To change the server or key: edit `config.rs` in the hbb_common fork, push to its
`matrixconnections` branch, then update the submodule pointer here
(`git submodule update --remote libs/hbb_common && git commit`) and re-run the workflow.

## Icons (Windows)
- `flutter/windows/runner/resources/app_icon.ico`: exe / taskbar icon
- `res/icon.ico`: installer + portable packer icon, MSI icon
- `res/tray-icon.ico`: system tray icon
- `res/icon.png`, `res/*.png`, `flutter/assets/icon.svg`: in-app logo
