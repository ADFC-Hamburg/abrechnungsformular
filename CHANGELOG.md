# Changelog

## Unreleased

### Changed

- Replaced letter symbol "a" in template with ADFC logo 
- In the web form, money amounts in cost positions are no longer colored red

## v1.7 - 2024-12-31

### Added

- Library libpango 1.0-0 is installed by itself (no longer as part of libgtk 3.0)

### Fixed

- Order of domain/subdomain of email address in instructions (form and template) swapped
- Positions treated like income after form reset
- Wrong path to nologin shell script for user appuser
- Fontconfig threw errors, lacked permissions to write to cache

### Changed

- Flask (Python dependency) updated to version 3.1
- Weasyprint (Python dependency) updated to version 63
- Updated Aktivenabrechnung.pdf (blank form PDF file)

### Removed

- Library libgtk 3.0 (was only used for libpango, which is now installed by itself)

## v1.6 - 2024-12-19

### Added
- Form validates IBAN length based on coutry code
- Form validates correct pattern for some country codes
- Contact/data protection links and version at bottom of form

### Changed
- Form input for IBAN no longer assumes country code DE
- PDF template no longer assumes country code DE
- Gendered form header
- Rewritten mialing instructions at bottom of form
- Minor changes to mailing instruction layout
- Swapped radio buttons income and expense; expense made default
- Rewritten instruction box in PDF document

### Removed
- Line on top of PDF file

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
