# Steam Pigeon locator hardware

KiCad 10 design for the Steam Pigeon rocket locator: an STM32WL5MOC LoRa module with GPS, IMU, barometer, flash, USB-C charging and four deployment channels. Firmware lives in [steam-pigeon-locator](https://github.com/fschroer/steam-pigeon-locator).

## Board at a glance

| Block | Parts |
| --- | --- |
| MCU and radio | STM32WL5MOCH6TR (U5), U.FL antenna (J7), high-power PA configuration |
| GPS | u-blox SAM-M10Q (U2), I2C2 at 0x42 |
| Sensors | ISM6HG256X IMU (U14), MS5611 barometer (U16), MX25L6436F flash (U17), all on SPI2 |
| Power | BQ25185 charger (U18), RT9080-33 LDO (U7), DRV5032 Hall sensor and 74HCS00 latch for magnet on/off |
| USB | USB-C (J1), CH340N serial (U4) |
| Deployment | Arm switch U13 (DMP2021UFDF) driven by DARM, four TPS22950 high-side switches plus PMXB43UNE (DFN1010D-3) low-side return switches (Q4-Q7) on J2 and J4; continuity sense DS1-DS4 on the return side |
| Audio | PAM8904 piezo driver (U11) |

Board size is 54 x 25 mm, 4 layers. The silkscreen carries the board revision (currently `SPL915STM B01`).

## Repository layout

| Path | Contents |
| --- | --- |
| `RocketLocator.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | The design |
| `lib/` | Project-local symbol and footprint libraries |
| `sym-lib-table`, `fp-lib-table` | Project library tables pointing into `lib/` |
| `BOM/RocketLocatorBOM.xlsx` | Purchasing BOM: JLCPCB part numbers, cost, stock and order tracking, plus a JLCPCB upload sheet. Maintained by hand; keep it in step with the schematic |
| `.github/workflows/kicad.yml` | ERC, DRC and fab outputs on every push |

Generated files (Gerbers, drill, BOM, CPL, netlist, PDF) are not committed. CI builds them on every push as a downloadable workflow artifact, and attaches them to a GitHub release when you push a board tag.

## Open design issues

Findings from the 2026-10-15 design review are tracked as GitHub issues. The full write-up is in the [RocketLocator design review](https://claude.ai/code/artifact/725ce922-3286-4f00-98c2-284a111a1c0e).

## Libraries

Non-stock parts live in `lib/` and are registered in the project's `sym-lib-table` and `fp-lib-table` with `${KIPRJMOD}` paths, so a fresh clone opens without any global library setup. Project entries override a global library with the same nickname.

| Library | Contents | Source |
| --- | --- | --- |
| `Custom.kicad_sym`, `Custom.pretty` | Project symbols and footprints | Copied from the personal KiCad 9.0 `Custom` libraries, 2026-10-15 |
| `RT9080-33GJ5.kicad_sym` | RT9080-33 LDO symbol | Extracted from the schematic's embedded symbol cache |
| `STM32WL5MOCH6TR.kicad_sym` | STM32WL5MOC module symbol | Extracted from the schematic's embedded symbol cache |
| `U.FL-R-SMT_01_.kicad_sym` | U.FL receptacle symbol | Extracted from the schematic's embedded symbol cache |

`Custom.pretty` also holds `SOT94P280X100-5N` (U7) and `SOP-8_5.28x5.23mm_P1.27mm` (U17). Their original libraries (`RT9080`, `Package_SO_New`) no longer existed, so they were recovered from the board file, converted back to front-side library form, and the design was relinked to `Custom:`.

When you change a part, edit it in `lib/` (not in your personal library) and commit it with the design change. All 3D models referenced by the footprints come from KiCad's stock 3D library.

## Releasing a board

1. Make sure ERC and DRC are clean.
2. Update the silkscreen revision and date.
3. Commit, then tag with the board revision and order date, for example `git tag B02-2026-11-20 && git push --tags`.
4. Download the Gerber zip, BOM and CPL from the release and upload them to the fab.

## Working copy

Keep the working copy outside Google Drive, OneDrive or Dropbox, because folder sync corrupts the `.git` directory. GitHub is the backup.
