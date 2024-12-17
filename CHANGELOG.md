# Changelog

## Unreleased

### Changed

- Gendered form header
- Rewritten mialing instructions at bottom of form
- Minor changes to mailing instruction layout

## v1.5 - 2024-12-10

### Added
- Invalid form inputs are highlighted
- Form validates IBAN input via checksum

### Changed
- Form button size on small screens

## v1.4 - 2024-12-05

### Added

- Form validates text inputs
- Error message for bad input (i.e. letters) in number input field

### Changed

- Personal name/group and project name/date input now required
- IBAN and account owner input now required (if Javascript is active)
- Streamlined HTML code (fewer span elements)
- Redesigned input elements (size and border)
- Minor layout improvements

### Fixed

- Date input, once confirmed invalid, cannot successfully validate

## v1.3 - 2024-12-03

### Added

- Web App Manifest
- Form validates number and date inputs
- Form validates that no position is filled in partially
- Form validates that at least one position or donation is filled in

### Changed

- Changed labels "Mengenpreis" to "Einzelpreis"
- Fields are now embedded in labels
- Multiline labels for radio buttons and checkboxes now indent properly
- Moved form events from HTML tags to JavaScript listeners

### Fixed

- Positions set to cost still treated like cost after form reset
- Form did not properly handle already filled fields when accessing via browser's back or forward

## v1.2 - 2024-11-26

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
