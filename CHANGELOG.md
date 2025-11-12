# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - v0.1.5

### Fixed
- **CRITICAL**: Corrected API endpoints to match official Elecnova ECO EMS Cloud API v1.3.1 documentation
  - `get_cabinets()`: Changed from undocumented `/api/v1/cabinet/list` to documented `/api/v1/dev`
  - `get_components()`: Changed from undocumented `/api/v1/cabinet/{sn}/components` to documented `/api/v1/dev/{sn}`
  - This fixes empty response issues caused by using incorrect endpoint paths

### Added
- Detailed error logging for empty/invalid API responses to aid debugging
- Comprehensive CHANGELOG.md for tracking version history

### Changed
- Enhanced documentation in README.md with migration guide and v1.3.1 API features

## [0.1.4] - 2025-11-12

### Fixed
- Handle empty API responses gracefully with proper error handling
- Improved resilience for cases where API returns no data

## [0.1.3] - 2025-11-12

### Fixed
- Apply ruff formatting across codebase for consistency
- Code style improvements

## [0.1.2] - 2025-11-12

### Fixed
- Remove unused imports (`generate_auth_headers`, `TokenResponse`)
- Fix line length violations (100 character limit)
- Linting improvements for CI/CD compliance

### Added
- Support for Elecnova ECO EMS Cloud API v1.3.1
- New `PowerDataPoint` model for PV power generation data
- Four new PV power generation methods:
  - `get_pv_power_cap()`: Get PV power with 5-minute intervals
  - `get_pv_power_gen_daily()`: Get PV daily generation (past 7 days)
  - `get_pv_power_gen_monthly()`: Get PV monthly daily generation
  - `get_pv_power_gen_yearly()`: Get PV annual monthly generation
- Optional `component` and `component_desc` fields to `Component` model (v1.3.1+)

### Changed
- Updated `Component` model with new v1.3.1 fields for component type codes
- Component type codes: `ess.ems`, `ess.bms`, `ess.pcs`, `pv.inv`, `ess.meter`, etc.
- Component descriptions: EMS, BMS, PCS, PV, Meter

## [0.1.0] - 2025-10-13

### Added
- Initial release of elecnova-client
- Async HTTP client (`ElecnovaClient`) for Elecnova ECO EMS Cloud API
- Synchronous client (`ElecnovaClientSync`) for non-async environments
- HMAC-SHA256 authentication with Bearer token support (24-hour TTL)
- Cabinet and component management:
  - `get_cabinets()`: Fetch ESS cabinets with pagination
  - `get_components()`: Fetch components for specific cabinet
- MQTT topic subscription:
  - `subscribe_mqtt_topics()`: Subscribe to MQTT topics for real-time data
- Exception handling:
  - `ElecnovaAPIError`: General API errors
  - `ElecnovaAuthError`: Authentication failures
  - `ElecnovaRateLimitError`: Rate limit exceeded (429)
  - `ElecnovaTimeoutError`: Request timeouts
- Pydantic models:
  - `Cabinet`: ESS cabinet information
  - `Component`: Component (BMS, PCS, Meter, etc.)
  - `TokenResponse`: Authentication token response
- Comprehensive README.md with usage examples
- Full test coverage with pytest
- CI/CD pipeline with GitHub Actions
- PyPI publication workflow

## [0.1.0-rc1] - 2025-10-13

### Added
- Release candidate for initial version
- All features from v0.1.0

---

[Unreleased]: https://github.com/elektriciteit-steen/elecnova-client/compare/v0.1.4...HEAD
[0.1.4]: https://github.com/elektriciteit-steen/elecnova-client/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/elektriciteit-steen/elecnova-client/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/elektriciteit-steen/elecnova-client/compare/v0.1.0...v0.1.2
[0.1.0]: https://github.com/elektriciteit-steen/elecnova-client/compare/v0.1.0-rc1...v0.1.0
[0.1.0-rc1]: https://github.com/elektriciteit-steen/elecnova-client/releases/tag/v0.1.0-rc1
