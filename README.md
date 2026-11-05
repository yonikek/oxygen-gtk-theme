# Oxygen GTK

A GTK 2/3/4 theme that gives GTK applications the look of KDE's **Oxygen**
style, while still being generated from the active KDE colour scheme.

It is derived from [Breeze GTK](https://invent.kde.org/plasma/breeze-gtk)
(GTK2 pixmaps originally by
[scionicspectre](https://github.com/scionicspectre/BreezyGTK)). The Breeze
build system, colour-scheme plumbing, named-colour API and widget structure
are kept; the visual layer has been rewritten to follow Oxygen.

| | |
|---|---|
| Theme names | `Oxygen` (light, with a `gtk-dark.css` that switches to the dark variant for `prefer-dark` apps) and `Oxygen-Dark` |
| Project / package id | `oxygen-gtk-theme` |

## What looks like Oxygen

* Lit vertical gradients on buttons, tool buttons, tabs, toolbars, titlebars,
  tooltips, selections and the top of every window.
* A dark 1px outline with a light inner bevel and a soft drop shadow on raised
  surfaces; pressed and checked states are sunken.
* Inset text fields, scale troughs, progress troughs and scrollbar grooves.
* Coloured glow rings in the scheme's *hover* and *focus* decoration colours.
* Raised scrollbar sliders in a groove, glossy selection-coloured progress bars
  and slider fills, raised check/radio boxes and round slider handles.
* Tighter 4px corner radius, thicker progress bars and slider troughs.

Every gradient, outline and highlight is expressed with GTK colour functions
(`shade()`, `alpha()`, `mix()`) on the exported named colours, so nothing is
hard-coded to one palette.

## Following the system colour scheme

This works exactly as it does in Breeze GTK:

* The theme is generated from a KDE colour scheme. By default
  (`build_theme.sh` with no `-c`) it is generated from `~/.config/kdeglobals`,
  i.e. the colour scheme currently active in Plasma. Re-run it after changing
  the scheme to regenerate the theme.
* `settings.ini` loads `colorreload-gtk-module` (from kde-gtk-config) so
  running GTK applications pick up colour changes.
* The standard GTK named colours (`theme_bg_color`, `theme_selected_bg_color`,
  ...) are still exported for applications that use them.
* `gtk-dark.css` makes the light theme import the dark variant for applications
  that request a dark theme.

Note: kde-gtk-config's automatic regeneration is tied to the `Breeze` theme
name, so it may not regenerate a theme called `Oxygen`. If the colours do not
follow a scheme change, run the script below yourself (e.g. from a hook that
fires when you change colour scheme).

## Build and install

Requirements: CMake, Extra CMake Modules, the Breeze package (for its stock
colour schemes), Python 3 with pycairo, and `sassc` (or `sass`).

```sh
cmake -B build -DCMAKE_INSTALL_PREFIX=/usr
cmake --build build
sudo cmake --install build        # installs Oxygen and Oxygen-Dark to share/themes
```

The static variants are generated from the `Oxygen` colour scheme if Plasma
provides it (otherwise `BreezeLight`) and from `BreezeDark`. Override with
`-DOXYGEN_GTK_LIGHT_SCHEME=...` / `-DOXYGEN_GTK_DARK_SCHEME=...`.

To generate the theme from your current Plasma colours, into
`~/.local/share/themes/Oxygen`:

```sh
cd src && ../build/src/build_theme.sh              # uses ~/.config/kdeglobals
cd src && ../build/src/build_theme.sh -c Oxygen    # or name a scheme
```

Then choose *Oxygen* in System Settings > Application Style > GNOME/GTK
Application Style (kde-gtk-config), or set `gtk-theme-name=Oxygen`. Make sure
"apply colours to non-Qt applications" is disabled if you want the theme's
own colours.

## Notes

* Requires GTK 3.16+, GTK 4, and the pixmap engine for GTK 2.
* The internal named-colour suffix is `_oxygen`; it is private to the theme.
* The SCSS was edited without access to a Sass compiler. If the build reports a
  Sass error, please open an issue with the message.

## Credits and licence

Based on Breeze GTK (KDE). Visual design follows the Oxygen style by the KDE
Oxygen team; no Oxygen source code is included. See `LICENSES/`.
