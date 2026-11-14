{
  lib,
  stdenv,
  cmake,
  kdePackages,
  python3,
  dart-sass,
}:

let
  # The static theme is generated from Plasma's stock colour schemes
  # (BreezeLight.colors, BreezeDark.colors), which the Breeze package installs.
  colorSchemes = "${kdePackages.breeze}/share/color-schemes";
in
stdenv.mkDerivation {
  pname = "oxygen-gtk-theme";
  version = "1.0.0";

  src = lib.fileset.toSource {
    root = ./.;
    fileset = lib.fileset.unions [
      ./CMakeLists.txt
      ./cmake
      (lib.fileset.difference ./src (lib.fileset.maybeMissing ./src/.sass-cache))
      ./LICENSES
    ];
  };

  nativeBuildInputs = [
    cmake
    kdePackages.extra-cmake-modules
    # render_assets.py draws the GTK2 pixmaps with pycairo
    (python3.withPackages (ps: [ ps.pycairo ]))
    # provides the `sass` binary that build_theme.sh uses when sassc is absent
    dart-sass
    kdePackages.wrapQtAppsHook
  ];

  # find_package(Breeze) in CMakeLists.txt
  buildInputs = [ kdePackages.breeze ];

  # BreezeConfig.cmake lives in the dev output while the colour schemes are in
  # the main one, so BREEZE_COLOR_INSTALL_ROOT would point at the wrong store
  # path. Name the real directory instead.
  postPatch = ''
    substituteInPlace src/CMakeLists.txt \
      --replace-fail "\''${BREEZE_COLOR_INSTALL_ROOT}" "${colorSchemes}"
  '';

  meta = {
    description = "GTK 2/3/4 theme in the style of KDE's Oxygen, following the KDE colour scheme";
    # derived from Breeze GTK (LGPL-2.1-or-later)
    license = lib.licenses.lgpl21Plus;
    platforms = lib.platforms.linux;
  };
}
