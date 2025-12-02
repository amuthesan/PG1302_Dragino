# Changelog

## [Unreleased]

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
