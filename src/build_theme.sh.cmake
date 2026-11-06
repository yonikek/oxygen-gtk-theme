#!/bin/sh
set -e

# Usage: create_folders <target-directory>
create_folders () {
  for j in gtk-2.0 gtk-3.0 gtk-4.0; do
    if ! [ -d "$1/$j" ]; then
        mkdir -p "$1/$j"
    fi
  done 
}

# Usage: build_sass <source-directory> <target-directory> <include-directory>
build_sass() {
  if command -v sassc >/dev/null 2>&1; then
      sassc -I "$3" "$1" "$2"
  elif sass --version 2>&1 | grep -qi ruby; then
      sass -I "$3" --cache-location /tmp/sass-cache "$1" "$2"
  else
      sass --no-source-map -I "$3" "$1" "$2"
  fi
}

# Usage: install_theme <theme-directory> <theme-name> <install-target-dir>
# If <install-target-dir> is unset or empty, install to $HOME/.local/share/themes/$THEME_NAME
install_theme () {
  THEME_INSTALL_TARGET="$3"
  if [ -z "${THEME_INSTALL_TARGET}" ]; then
    THEME_INSTALL_TARGET="${HOME}/.local/share/themes/$2"
  fi
  echo "Installing into ${THEME_INSTALL_TARGET}"
  mkdir -p "${THEME_INSTALL_TARGET}"
  for dir in assets gtk-2.0 gtk-3.0 gtk-4.0; do
    if [ -d "${THEME_INSTALL_TARGET}/$dir" ]; then
      rm -rf "${THEME_INSTALL_TARGET:?}/$dir"
    fi
    mv -f "$1/$dir" "${THEME_INSTALL_TARGET}"
  done
  rmdir "$1"
}

# Usage render_theme <colorscheme> <theme-name> <theme-install-target> <colorschemebase>
render_theme () {
  THEME_BUILD_DIR="$(mktemp -d)"
  create_folders "${THEME_BUILD_DIR}"
  cp -R gtk2/* "${THEME_BUILD_DIR}/gtk-2.0/"
  @Python3_EXECUTABLE@ render_assets.py -c "$1" -a "${THEME_BUILD_DIR}/assets" \
    -g "${THEME_BUILD_DIR}/gtk-2.0" -G "${THEME_BUILD_DIR}" -b "$4"
  build_sass gtk3/gtk.scss "${THEME_BUILD_DIR}/gtk-3.0/gtk.css" "${THEME_BUILD_DIR}"
  build_sass gtk4/gtk.scss "${THEME_BUILD_DIR}/gtk-4.0/gtk.css" "${THEME_BUILD_DIR}"
  rm -f "${THEME_BUILD_DIR}/_global.scss"
  install_theme "${THEME_BUILD_DIR}" "$2" "$3"
}

COLOR_SCHEME=""
INSTALL_TARGET=""
THEME_NAME=""
DARK_SCHEME=""
COLOR_SCHEME_ROOT="/usr/share/color-schemes"

while [ "$#" -gt 0 ]; do
  case "$1" in
    -h|--help)
      echo "$0: build Oxygen GTK theme"
      echo "Usage: $0 [-c COLOR_SCHEME] [-d DARK_SCHEME] [-r COLOR_SCHEME_ROOT] [-t TARGET_DIRECTORY]"
      echo
      echo "Arguments:"
      echo "  -h, --help           show this help"
      echo "  -c COLOR_SCHEME      use color scheme with name COLOR_SCHEME. If unset or"
      echo "                       empty, the value from ~/.config/kdeglobals is used"
      echo "  -d DARK_SCHEME       additionally write gtk-dark.css built from"
      echo "                       DARK_SCHEME into the theme. If unset or empty,"
      echo "                       BreezeDark is used"
      echo "  -r COLOR_SCHEME_ROOT The base path of all color schemes or"
      echo "                       /usr/share/color-schemes if unset"
      echo "  -t TARGET_DIRECTORY  the directory to install the color scheme. If unset or"
      echo "                       empty, it is installed into"
      echo "                       ~/.local/share/themes/THEME_NAME"
      exit 0
    ;;
    -c)
      shift
      COLOR_SCHEME="$1"
    ;;
    -d)
      shift
      DARK_SCHEME="$1"
    ;;
    -t)
      shift
      INSTALL_TARGET="$1"
    ;;
    -r)
      shift
      COLOR_SCHEME_ROOT="$1"
    ;;
  esac
  shift
done

if [ -z "${COLOR_SCHEME}" ]; then
  THEME_NAME="Oxygen"
  if [ -f "${HOME}/.config/kdeglobals" ]; then
    COLOR_SCHEME="${HOME}/.config/kdeglobals"
  else
    echo "${HOME}/.config/kdeglobals not found, using defaults"
    COLOR_SCHEME="${COLOR_SCHEME_ROOT}/BreezeLight.colors"
  fi
else
  THEME_NAME="${COLOR_SCHEME}"
  if [ -f "${COLOR_SCHEME_ROOT}/${COLOR_SCHEME}.colors" ]; then
    COLOR_SCHEME="${COLOR_SCHEME_ROOT}/${COLOR_SCHEME}.colors"
  elif [ -f "${HOME}/.local/share/color-schemes/${COLOR_SCHEME}.colors" ]; then
    COLOR_SCHEME="${HOME}/.local/share/color-schemes/${COLOR_SCHEME}.colors"
  else
    echo "colorscheme ${COLOR_SCHEME} not found"
    exit 1
  fi
fi

render_theme "${COLOR_SCHEME}" "${THEME_NAME}" "${INSTALL_TARGET}" "${COLOR_SCHEME_ROOT}/BreezeLight.colors"
[ -z "${INSTALL_TARGET}" ] && INSTALL_TARGET="${HOME}/.local/share/themes/${THEME_NAME}"
cp -r assets/ "${INSTALL_TARGET}"

# Optional dark fallback: a full build from the given scheme written as
# gtk-dark.css into the same theme folder (used when an app requests a dark
# preference and no Plasma-provided colours are around).
if [ -n "${DARK_SCHEME}" ]; then
  DARK_FILE="${COLOR_SCHEME_ROOT}/${DARK_SCHEME}.colors"
  if ! [ -f "${DARK_FILE}" ]; then
    DARK_FILE="${HOME}/.local/share/color-schemes/${DARK_SCHEME}.colors"
  fi
  if ! [ -f "${DARK_FILE}" ]; then
    echo "colorscheme ${DARK_SCHEME} not found"
    exit 1
  fi
  DARK_STAGING="$(mktemp -d)"
  render_theme "${DARK_FILE}" "${THEME_NAME}" "${DARK_STAGING}" "${COLOR_SCHEME_ROOT}/BreezeLight.colors"
  cp "${DARK_STAGING}/gtk-3.0/gtk.css" "${INSTALL_TARGET}/gtk-3.0/gtk-dark.css"
  cp "${DARK_STAGING}/gtk-4.0/gtk.css" "${INSTALL_TARGET}/gtk-4.0/gtk-dark.css"
  rm -rf "${DARK_STAGING}"
fi
