# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-10-15

### Added
- **Elecnova API V2.2.0 project → site → device hierarchy** (released 2026-09-28, live
  2026-10-15). Backwards compatible: no existing method or model changed.
  - `get_projects()` — `GET /api/v2/projects`, returns `list[Project]`
  - `get_project_sites(project_id, page=1, page_size=100)` — `GET /api/v2/project/{id}/sites`,
    returns `list[Site]` for the requested page; logs a warning when `total_count`
    exceeds the page, so a short page cannot pass for the whole set
  - `get_site_devices(site_id)` — `GET /api/v2/site/{id}/devices`, returns `list[Device]`
  - All three are on the async `ElecnovaClient` and the sync `ElecnovaClientSync`
- New models: `Project`, `Site`, `Device`, `Pagination`, `PaginatedV2Response`
- Join keys (verified live 2026-10-15):
  - `Site.id` is the same UUID as the station ID in the Elecnova web UI — a durable
    join key for site attribution, unlike the name
  - `Device.id` is the same UUID as `Cabinet.id` from `GET /api/v1/dev`, so the v2
    hierarchy joins cleanly onto the existing v1 surface

### Notes
- **Response shapes differ per endpoint.** `/api/v2/projects` and
  `/api/v2/site/{id}/devices` answer with a **bare JSON array**;
  `/api/v2/project/{id}/sites` answers with `{"data": [...], "pagination": {...}}`.
  Neither uses the `{code,message,data}` envelope of some v1 endpoints.
- **The v2 endpoints name their fields in snake_case** (`time_zone`, `begin_at`,
  `rated_power`, `page_size`, `total_count`), unlike v1 which is camelCase for some
  fields (`timeZone`, `lastSeen`). The models follow the wire format rather than
  normalising it, so `Site.time_zone` has no `timeZone` alias.

### Fixed
- `__init__.__version__` was stale at `0.1.6` while `pyproject.toml` read `0.2.2`; both
  now read `0.3.0`.

## [0.2.0] - 2025-11-13

### Breaking Changes
- **`subscribe_mqtt_topics()` signature changed**:
  - Parameter `device_id` renamed to `mqtt_client_id` (clarifies it's the MQTT Client ID from `/comm/client`)
  - Added `mode` parameter (1=cabinet level, 2=component level, default: 1)
  - Old: `subscribe_mqtt_topics(device_id, sn)`
  - New: `subscribe_mqtt_topics(mqtt_client_id, sn, mode=1)`

### Added
- **`get_mqtt_credentials()` method**: Fetch MQTT broker credentials from `/comm/client` endpoint
  - Returns: `{"id": "...", "username": "...", "password": "...", "token": "..."}`
  - Use `id` field as `mqtt_client_id` parameter for `subscribe_mqtt_topics()`
  - Username/password for MQTT broker connection
  - Token for authenticated API calls

### Changed
- `subscribe_mqtt_topics()`: Now accepts cabinet or component serial numbers based on `mode` parameter
- MQTT subscription endpoint now includes mode query parameter: `/api/v1/dev/topic/{mqtt_client_id}/{sn}?mode={mode}`
- Improved logging to show number of topics returned from subscription

## [0.1.6] - 2025-11-12

### Fixed
- **CRITICAL**: Corrected business API authentication to match Elecnova ECO EMS Cloud API specification
  - Authorization header now uses **raw token** (no "Bearer " prefix)
  - Business APIs now include **all required headers**: `Authorization`, `X-Access-ID`, `X-Timestamp`, `X-Signature`, `X-Language-Type`
  - MQTT subscription endpoint changed from POST to GET (`/api/v1/dev/topic/{id}/{sn}`)
  - Response validation now handles raw data responses (without `code` wrapper)
  - This fixes "access id is required" and "access token is invalid" errors

### Added
- Cabinet model: Added `id` field (UUID from API response)
- Component model: Added `id` field (UUID from API response)

### Changed
- Component model: `state` field changed from `str` to `bool` (matches API response format)
- Response handling: More flexible validation for endpoints that return raw lists/dicts
- `get_cabinets()`: Simplified to handle raw list response (not wrapped in ApiResponse)
- `get_components()`: Extracts components from `parts` array in cabinet response
- Authentication: All business API requests now use complete signature + token authentication

## [0.1.5] - 2025-11-12

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
- Version corrected from 0.1.2 to 0.1.5 (after v0.1.4 release)

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
