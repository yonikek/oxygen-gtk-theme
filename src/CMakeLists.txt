file(GLOB_RECURSE SCSS_SOURCES "*.scss")
file(GLOB CSS_SOURCES "*.css")
file(GLOB_RECURSE GTK2_SOURCES "gtk2/*")

configure_file(build_theme.sh.cmake ${CMAKE_CURRENT_BINARY_DIR}/build_theme.sh @ONLY)

set(SOURCES
    ${SCSS_SOURCES}
    ${CSS_SOURCES}
    ${GTK2_SOURCES}
    render_assets.py
)

# Colour schemes the static (pre-built) variants are generated from. The
# Oxygen scheme ships with Plasma; fall back to Breeze Light if it is absent.
if(EXISTS "${BREEZE_COLOR_INSTALL_ROOT}/Oxygen.colors")
    set(OXYGEN_GTK_LIGHT_SCHEME "Oxygen" CACHE STRING "Colour scheme for the light variant")
else()
    set(OXYGEN_GTK_LIGHT_SCHEME "BreezeLight" CACHE STRING "Colour scheme for the light variant")
endif()
set(OXYGEN_GTK_DARK_SCHEME "BreezeDark" CACHE STRING "Colour scheme for the dark variant")

# A single "Oxygen" theme folder is installed. Its gtk.css/gtk-4.0/gtk.css are
# built from the light scheme; gtk-dark.css (both toolkits) is a full build from
# the dark scheme for apps requesting a dark preference outside Plasma. On
# Plasma the runtime colours from kde-gtk-config (colors.css) override all
# named colours anyway, so the single theme follows the active colour scheme.

set(OXYGEN_GTK_DARK_SCHEME "BreezeDark" CACHE STRING "Colour scheme for the dark fallback variant")

set(OXYGEN_THEME_DIR "${PROJECT_BINARY_DIR}/Oxygen")
# intermediate build directory for the dark fallback css
set(OXYGEN_DARK_STAGING "${PROJECT_BINARY_DIR}/Oxygen-dark-staging")

set(Oxygen_TARGETS
    "${OXYGEN_THEME_DIR}/gtk-2.0/gtkrc"
    "${OXYGEN_THEME_DIR}/gtk-3.0/gtk.css"
    "${OXYGEN_THEME_DIR}/gtk-3.0/gtk-dark.css"
    "${OXYGEN_THEME_DIR}/gtk-4.0/gtk.css"
    "${OXYGEN_THEME_DIR}/gtk-4.0/gtk-dark.css"
)

add_custom_command(
    OUTPUT ${Oxygen_TARGETS}
    DEPENDS ${SOURCES} ${CMAKE_CURRENT_BINARY_DIR}/build_theme.sh
    COMMAND ${CMAKE_CURRENT_BINARY_DIR}/build_theme.sh -c ${OXYGEN_GTK_LIGHT_SCHEME} -t "${OXYGEN_THEME_DIR}" -r "${BREEZE_COLOR_INSTALL_ROOT}"
    COMMAND ${CMAKE_CURRENT_BINARY_DIR}/build_theme.sh -c ${OXYGEN_GTK_DARK_SCHEME} -t "${OXYGEN_DARK_STAGING}" -r "${BREEZE_COLOR_INSTALL_ROOT}"
    COMMAND cp "${OXYGEN_DARK_STAGING}/gtk-3.0/gtk.css" "${OXYGEN_THEME_DIR}/gtk-3.0/gtk-dark.css"
    COMMAND cp "${OXYGEN_DARK_STAGING}/gtk-4.0/gtk.css" "${OXYGEN_THEME_DIR}/gtk-4.0/gtk-dark.css"
    COMMAND rm -rf "${OXYGEN_DARK_STAGING}"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src"
)
add_custom_target(Oxygen ALL DEPENDS ${Oxygen_TARGETS})

install(DIRECTORY "${OXYGEN_THEME_DIR}" DESTINATION "${KDE_INSTALL_FULL_DATAROOTDIR}/themes/")
install(FILES settings.ini DESTINATION "${KDE_INSTALL_FULL_DATAROOTDIR}/themes/Oxygen")
