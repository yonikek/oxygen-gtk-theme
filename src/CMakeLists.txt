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

function(gen_targets THEME_NAME)
    set(THEME_DIR "${PROJECT_BINARY_DIR}/${THEME_NAME}")
    set(${THEME_NAME}_TARGETS
        "${THEME_DIR}/gtk-2.0/gtkrc"
        "${THEME_DIR}/gtk-3.0/gtk.css"
        PARENT_SCOPE
    )
endfunction()

gen_targets(Oxygen)
gen_targets(Oxygen-Dark)

list(APPEND Oxygen_TARGETS
    "${PROJECT_BINARY_DIR}/Oxygen/gtk-3.0/gtk-dark.css"
    "${PROJECT_BINARY_DIR}/Oxygen/gtk-4.0/gtk-dark.css"
)

add_custom_command(
    OUTPUT ${Oxygen-Dark_TARGETS}
    DEPENDS ${SOURCES} ${CMAKE_CURRENT_BINARY_DIR}/build_theme.sh
    COMMAND ${CMAKE_CURRENT_BINARY_DIR}/build_theme.sh -c ${OXYGEN_GTK_DARK_SCHEME} -t "${PROJECT_BINARY_DIR}/Oxygen-Dark" -r "${BREEZE_COLOR_INSTALL_ROOT}"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src"
)
add_custom_target(Oxygen-Dark ALL DEPENDS ${Oxygen-Dark_TARGETS})

add_custom_command(
    OUTPUT ${Oxygen_TARGETS}
    DEPENDS ${SOURCES} ${CMAKE_CURRENT_BINARY_DIR}/build_theme.sh
    COMMAND ${CMAKE_CURRENT_BINARY_DIR}/build_theme.sh -c ${OXYGEN_GTK_LIGHT_SCHEME} -t "${PROJECT_BINARY_DIR}/Oxygen" -r "${BREEZE_COLOR_INSTALL_ROOT}"
    COMMAND cp gtk-dark-3.0.css "${PROJECT_BINARY_DIR}/Oxygen/gtk-3.0/gtk-dark.css"
    COMMAND cp gtk-dark-4.0.css "${PROJECT_BINARY_DIR}/Oxygen/gtk-4.0/gtk-dark.css"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}/src"
)
add_custom_target(Oxygen ALL DEPENDS ${Oxygen_TARGETS})

install(DIRECTORY "${PROJECT_BINARY_DIR}/Oxygen" DESTINATION "${KDE_INSTALL_FULL_DATAROOTDIR}/themes/")
install(DIRECTORY "${PROJECT_BINARY_DIR}/Oxygen-Dark" DESTINATION "${KDE_INSTALL_FULL_DATAROOTDIR}/themes/")
install(FILES settings.ini DESTINATION "${KDE_INSTALL_FULL_DATAROOTDIR}/themes/Oxygen")
install(FILES settings.ini DESTINATION "${KDE_INSTALL_FULL_DATAROOTDIR}/themes/Oxygen-Dark")
