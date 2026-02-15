# Changelog

## UNRELEASED

### Changed

- Colors in logos and web forms replaced with official ADFC colors
- Effect when hovering over web form buttons replaced with underline
- Changed border and background color of fieldset elements in web form
- Filename extension .j2 added to Jinja2 template files
- Removed garbage data from Docker image
- Improved color detection of semi-white logo generation

### Fixed

- Download button for blank PDF form no longer draggable
- Web forms will no longer (attempt to) load SVG and PNG version of logo at the same time

## v2.8 - 2026-01-26

### Changed

- Base image updated to Alpine 3.23
- Python updated to version 3.14.2
- Weasyprint (Python dependency) updated to version 68

## v2.7 - 2025-12-08

### Changed

- Date fields no longer restrict entering dates beyond the present day
- Changed instructions for sending in the finished document in form Reisekostenabrechnung to match form Aktivenabrechnung

## v2.6 - 2025-11-27

### Added

- Use environment variable to store version number (set during Docker build with `--build-arg VERSION=`)
- Store git tag as version number when building via GitHub workflow run

### Changed

- Drafthorse (Python dependency) updated to version 2025.2
- Weasyprint (Python dependency) updated to version 66
- Schwifty (Python dependency) updated to version 2025.9
- Remove brackets surrounding the date from the project name in Aktivenabrechnung e-invoices

### Fixed

- ADFC bank account information is now written into payer field, not payee field, in Reisekostenabrechnung e-invoices

### Removed

- VERSION file

## v2.5 - 2025-10-13

### Added

- Added buttons to web form for swapping positions

### Changed

- Reset position buttons in web form now remove the position and move lower positions up
- Enlarged position reset button slightly

### Fixed

- Position remove buttons now render correctly regardless of available fonts

## v2.4 - 2025-09-30

### Added

- Added buttons to web form for resetting individual positions

### Changed

- Underlying Linux image changed from Debian-slim to Alpine
- Package index update, package installation and index/cache cleaning are combined into a single layer in the docker image
- Minor changes to web form layout

### Fixed

- Removed warning about running pip as root user during docker build process

## v2.3 - 2025-06-02

### Changed

- Position names in PDF files will never be abbreviated
- Size of some text fields in PDF files (position names, IBANs, account names) are shrunk if text exceeds a certain length

### Fixed

- IBAN and account owner fields in Antragsformular PDF file can no longer be wider than intended

## v2.2 - 2025-05-15

### Fixed

- Blank PDF file generation works now

## v2.1 - 2025-05-15

### Added

- Generate blank PDF files and white variants of company logo as part of the docker build process
- Can now use PNG files for company logo in place of SVG files

### Changed

- Weasyprint (Python dependency) updated to version 65
- Reworded parts of the web forms and Reisekosten PDF form
- Cut off decimal places from whole Euro amounts in rate listings in Reisekosten PDF form

### Removed

- Blank PDF files (now generated during docker build)
- White variants of ADFC logo (now generated during docker build)

## v2.0 - 2025-04-29

### Added

- Second web form for generating travel expense invoices
- Config file

### Changed

- All mentions of ADFC Hamburg (except the logo) can now be replaced via config

### Removed

- CONTACT.json (replaced by CONFIG.ini)

## v1.12 - 2025-03-17

### Fixed

- HTML code in user-submitted text is now properly escaped again

## v1.11 - 2025-03-11

### Added

- Jinja (Python dependency) specifically part of requirements (was already included as part of flask)

### Changed

- Template for PDF now handled via jinja
- Web form gets mail and link addresses from contact file
- Gendering in PDF template

### Removed

- Class aktive.HTMLPrinter removed (functionality folded into class aktive.Abrechnung)

## v1.10 - 2025-02-25

### Changed

- Improved form initialization routine

### Fixed

- Can no longer submit web form without payment option selected

## v1.9 - 2025-02-18

### Added

- Server-side verification of submitted web form

### Fixed

- Form can now require SEPA mandate info to submit
- Positions set to income no longer treated as income after web form reset

## v1.8 - 2025-02-13

### Added

- Add a Factur-X 1.0.06 (a.k.a. ZUGFeRD 2.2) compliant e-invoice to generated PDF files
- Hint in signature box when signature is not required

### Changed

- Weasyprint (Python dependency) updated to version 64
- Babel (Python dependency) updated to version 2.17
- Replaced letter symbol "a" in template for PDF with ADFC logo
- Reworked instructions for sending in the finished document
- In the web form, money amounts in cost positions are no longer colored red

### Removed

- Python library flask-weasyprint

## v1.7 - 2024-12-31

### Added

- Library libpango 1.0-0 is installed by itself (no longer as part of libgtk 3.0)

### Fixed

- Order of domain/subdomain of email address in instructions (web form and template) corrected
- Positions set to income no longer treated as income after web form reset
- Path to nologin shell script for user appuser fixed
- Fontconfig no longer throws errors due to lacking permissions to write to cache

### Changed

- Flask (Python dependency) updated to version 3.1
- Weasyprint (Python dependency) updated to version 63
- Updated Aktivenabrechnung.pdf (blank form PDF file)

### Removed

- Library libgtk 3.0 (was only used for libpango, which is now installed by itself)

## v1.6 - 2024-12-19

### Added
- Web form validates IBAN length based on coutry code
- Web form validates correct pattern for some country codes
- Contact/data protection links and version at bottom of web form

### Changed
- Web form input for IBAN no longer assumes country code DE
- PDF template no longer assumes country code DE
- Gendered web form header
- Rewritten mialing instructions at bottom of web form
- Minor changes to mailing instruction layout
- Swapped radio buttons income and expense; expense made default
- Rewritten instruction box in PDF document

### Removed
- Line on top of PDF file

## v1.5 - 2024-12-10

### Added
- Invalid web form inputs are highlighted
- Web form validates IBAN input via checksum

### Changed
- Web form button size on small screens

## v1.4 - 2024-12-05

### Added

- Web form validates text inputs
- Error message for bad input (i.e. letters) in number input field

### Changed

- Personal name/group and project name/date input now required
- IBAN and account owner input now required (if Javascript is active)
- Streamlined HTML code (fewer span elements)
- Redesigned input elements (size and border)
- Minor layout improvements

### Fixed

- Previously invalid Date input can now successfully validate

## v1.3 - 2024-12-03

### Added

- Web App Manifest
- Web form validates number and date inputs
- Web form validates that no position is filled in partially
- Web form validates that at least one position or donation is filled in

### Changed

- Changed labels "Mengenpreis" to "Einzelpreis"
- Fields are now embedded in labels
- Multiline labels for radio buttons and checkboxes now indent properly
- Moved web form events from HTML tags to JavaScript listeners

### Fixed

- Positions set to cost no longer treated as cost after web form reset
- Web form now properly handles already filled fields when accessing via browser's back or forward

## v1.2 - 2024-11-26

### Added

- Button to download blank PDF file added to web form
- Date field restricts entering dates beyond the present day

### Changed

- Reset button in web form labeled and colored red
- Logo in web form now handled via CSS
- Minor changes to web form header layout
- Invoice has '1' in unit count if valid position does not have a price per unit

### Fixed

- Can now submit web form with invalid IBAN entered while IBAN field is hidden/disabled
- Money total now updates when position is switched between income and cost

## v1.1 - 2024-11-21

### Added

- Version number is now printed on resulting PDF document.

### Changed

- Input fields for unit prices in web form now have red text when position is set to expense
- Changed email adress for sending in documents
- Positions in web form now automatically switch between multi-unit and single-unit
- Providing version number is now handled by app module itself

### Removed

- Checkboxes in web form to manually activate multi-unit positions
- Disabled revealing script-only elements in web form (no longer needed)

## v1.0 - 2024-11-19

First Release
