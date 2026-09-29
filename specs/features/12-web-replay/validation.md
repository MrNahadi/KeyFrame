# 12 Web demo: replay: validation

## Automated

1. `npm --prefix web test` and `npm --prefix web run build` pass; Python feedback commands still pass.
2. The token test passes (no raw colours in components).

## Manual (owner)

- `npm --prefix web run dev` with the API not running: pick "Turbine degradation at 85% load", press play at 60x, and read when the alarm fired. Check phone width and dark mode.
- Screenshots of the replay screen at 390 px and 1440 px, light and dark, are checked against Part 15 during validation.
