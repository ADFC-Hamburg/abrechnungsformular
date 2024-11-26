# Changelog

## Unreleased

### Added

- Button to download blank PDF file added to form
- Date field restricts entering dates beyond the present day

### Changed

- Reset button in form labeled and colored red
- Logo in form now handled via CSS
- Minor changes to form header layout
- Invoice has '1' in unit count if valid position does not have a price per unit

### Fixed

- Could not submit form with invalid IBAN entered even when IBAN field was hidden
- Money total did not update when position was switched between income and expense

## v1.1 - 2024-11-21

### Added

- Version number is now printed on resulting PDF document.

### Changed

- Input fields for unit prices in form now have red text when position is set to expense
- Changed email adress for sending in documents
- Positions in form now automatically switch between multi-unit and single-unit
- Providing version number is now handled by app module itself

### Removed

- Checkboxes in form to manually activate multi-unit positions
- Disabled revealing script-only elements in form (no longer needed)

## v1.0 - 2024-11-19

First Release
