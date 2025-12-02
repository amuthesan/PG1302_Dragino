# Changelog

## [Unreleased]

## [v0.1.2] - 2025-12-02

### Changed
- Updated UI status indicators: "Disconnected" status now displays in red for better visibility.

## [v0.1.1-beta] - 2025-12-02

### Added
- Implement web GUI for Dragino PG1302 gateway setup, including backend, frontend, and deployment scripts.
- Support dynamic IP address for deployment scripts and documentation.
- Support for separate LNS and CUPS API keys in Web UI.

### Fixed
- Corrected Gateway EUI generation to produce valid 8-byte EUI-64.
- Fixed installation failure when `draginofwd.deb` already exists.
- Fixed "No such file or directory" error for `station` binary by creating a symlink.
- Handled missing log file gracefully in status check.
- Ensured CA certificate permissions are set correctly.
